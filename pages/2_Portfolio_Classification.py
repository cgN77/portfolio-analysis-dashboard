import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def extract_asset_classifications(file_path, sheet_name="Sheet1"):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df.set_index("Name").to_dict(orient="index")

import pandas as pd

def create_sunburst_table(assets, total_portfolio_value, asset_classifications):
    data = []
    classification_totals = {}

    for asset, alloc_pct in assets.items():
        classification = asset_classifications.get(asset, {}).get("Classification", "Alternative")
        asset_class = asset_classifications.get(asset, {}).get("Asset Class", "")
        sub_asset_class = asset_classifications.get(asset, {}).get("Sub-Asset Class", "")
        liquidity = asset_classifications.get(asset, {}).get("Liquidity", "Illiquid")
        instrument = asset_classifications.get(asset, {}).get("Instrument/Manager", asset)
        allocation_value = (alloc_pct / 100.0) * total_portfolio_value

        # Store allocation sums for categories
        classification_totals.setdefault(classification, {}).setdefault(asset_class, {}).setdefault(sub_asset_class, [])
        classification_totals[classification][asset_class][sub_asset_class].append(
            {"Instrument/Manager": instrument, "Liquidity": liquidity, "Allocation (%)": alloc_pct, "Allocation ($)": allocation_value}
        )

    # Creating the hierarchical structure
    hierarchy_rows = []
    for classification, asset_classes in classification_totals.items():
        hierarchy_rows.append([classification, "", "", "", "", None, None])  # Classification row
        for asset_class, sub_classes in asset_classes.items():
            hierarchy_rows.append(["", asset_class, "", "", "", None, None])  # Asset Class row
            for sub_asset_class, instruments in sub_classes.items():
                hierarchy_rows.append(["", "", sub_asset_class, "", "", None, None])  # Sub-Asset Class row
                for instrument_data in instruments:
                    hierarchy_rows.append(["", "", "", instrument_data["Liquidity"], instrument_data["Instrument/Manager"], 
                                           instrument_data["Allocation (%)"], instrument_data["Allocation ($)"]])

    df_hierarchy = pd.DataFrame(hierarchy_rows, columns=["Classification", "Asset Class", "Sub-Asset Class", 
                                                          "Liquidity", "Instrument/Manager", "Allocation (%)", "Allocation ($)"])

    # Ensure numeric columns are correct
    # df_hierarchy["Allocation (%)"] = pd.to_numeric(df_hierarchy["Allocation (%)"], errors="coerce").fillna(0)
    # df_hierarchy["Allocation ($)"] = pd.to_numeric(df_hierarchy["Allocation ($)"], errors="coerce").fillna(0)

    return df_hierarchy



st.set_page_config(page_title="Fund Classification", layout="wide")
st.title("Portfolio Classification Dashboard")

def load_fund_names(file_path="input.xlsx"):
    """Load available Names from database"""
    return pd.read_excel(file_path)["Name"].unique().tolist()

def plot_sunburst_table(df):
    """Create table with color gradient based on allocation percentages"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis("off")
    
    # Create custom color gradient from yellow (0%) -> green (10%) -> dark red (50%)
    colors = [
        (0.0, "#FFFF00"),   # Yellow
        (0.2, "#00FF00"),   # Green (at 10% of 50% scale)
        (1.0, "#8B0000")   # Dark red
    ]
    cmap = mcolors.LinearSegmentedColormap.from_list("alloc_cmap", colors)
    norm = mcolors.Normalize(vmin=0, vmax=50)  # Scale up to 50%
    
    # Create base table
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
        colColours=["#2c3e50"]*len(df.columns)
    )
    
    # Apply color coding
    for i in range(1, len(df)+1):
        alloc_pct = df.iloc[i-1]["Allocation (%)"]
        
        # Get color from gradient
        scaled_value = min(alloc_pct, 50)  # Cap at 50% for coloring
        rgba = cmap(norm(scaled_value))
        hex_color = mcolors.to_hex(rgba, keep_alpha=False)
        
        # Apply to allocation cells
        table[(i, 5)].set_facecolor(hex_color)  # Allocation % column
        table[(i, 5)].get_text().set_color("white" if alloc_pct > 15 else "black")
        
        # Apply to dollar allocation column as well
        table[(i, 6)].set_facecolor(hex_color)
        table[(i, 6)].get_text().set_color("white" if alloc_pct > 15 else "black")

    # Header styling
    for j in range(len(df.columns)):
        table[(0, j)].set_facecolor("#2c3e50")
        table[(0, j)].get_text().set_color("white")
        table[(0, j)].set_fontsize(12)

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(df.columns))))
    
    st.pyplot(fig)

def main():
    # Load Names from database
    available_funds = load_fund_names()
    
    # Fund selection and allocation input
    selected_funds = st.multiselect("Select Funds", available_funds)
    
    if selected_funds:
        st.subheader("Enter Allocations")
        allocations = {}
        total_alloc = 0
        
        # Create input fields for each selected fund
        for fund in selected_funds:
            alloc = st.number_input(
                f"Allocation % for {fund}",
                min_value=0.0,
                max_value=100.0 - total_alloc,
                value=0.0,
                step=0.5
            )
            allocations[fund] = alloc
            total_alloc += alloc
        
        # Portfolio value input
        total_portfolio_value = st.number_input(
            "Total Portfolio Value ($)",
            value=1_000_000,
            min_value=0
        )
        
        if total_alloc > 0:
            # Load classifications and create table
            asset_classifications = extract_asset_classifications("input.xlsx")
            hierarchical_df = create_sunburst_table(
                allocations,
                total_portfolio_value,
                asset_classifications
            )
            
            st.subheader("Portfolio Classification")
            plot_sunburst_table(hierarchical_df)
            
            # Add download button
            csv = hierarchical_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                data=csv,
                file_name="portfolio_breakdown.csv",
                mime="text/csv"
            )
        else:
            st.warning("Please enter allocation percentages for selected funds")
    else:
        st.info("Please select funds to begin portfolio construction")

if __name__ == "__main__":
    main()