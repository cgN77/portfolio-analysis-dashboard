import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def extract_asset_classifications(file_path, sheet_name="Sheet1"):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df.set_index("Name").to_dict(orient="index")

import pandas as pd




st.set_page_config(page_title="Fund Classification", layout="wide")
st.title("Portfolio Classification Dashboard")

def load_fund_names(file_path="input.xlsx"):
    """Load available Names from database"""
    return pd.read_excel(file_path)["Name"].unique().tolist()

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

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

        classification_totals.setdefault(classification, {}).setdefault(asset_class, {}).setdefault(sub_asset_class, [])
        classification_totals[classification][asset_class][sub_asset_class].append({
            "Instrument/Manager": instrument, "Liquidity": liquidity,
            "Allocation (%)": alloc_pct, "Allocation ($)": allocation_value
        })

    hierarchy_rows = []

    for classification, asset_classes in classification_totals.items():
        classification_alloc_pct = 0
        classification_alloc_dollar = 0

        for asset_class in asset_classes.values():
            for sub_class in asset_class.values():
                for instrument in sub_class:
                    classification_alloc_pct += instrument["Allocation (%)"]
                    classification_alloc_dollar += instrument["Allocation ($)"]

        hierarchy_rows.append([classification, "", "", "", "", round(classification_alloc_pct, 2), round(classification_alloc_dollar, 2)])

        for asset_class, sub_classes in asset_classes.items():
            hierarchy_rows.append(["", asset_class, "", "", "", None, None])
            for sub_asset_class, instruments in sub_classes.items():
                hierarchy_rows.append(["", "", sub_asset_class, "", "", None, None])
                for instrument_data in instruments:
                    hierarchy_rows.append([
                        "", "", "", instrument_data["Liquidity"], instrument_data["Instrument/Manager"],
                        instrument_data["Allocation (%)"], instrument_data["Allocation ($)"]
                    ])

    df_hierarchy = pd.DataFrame(hierarchy_rows, columns=[
        "Classification", "Asset Class", "Sub-Asset Class", "Liquidity",
        "Instrument/Manager", "Allocation (%)", "Allocation ($)"
    ])
    return df_hierarchy


from st_aggrid import GridOptionsBuilder, AgGrid, JsCode

from st_aggrid import GridOptionsBuilder, AgGrid, JsCode

def plot_aggrid_table(df):
    # Add RowType classification
    def is_empty(val):
        return pd.isna(val) or val == ""

    def classify_row(row):
        if not is_empty(row["Classification"]) and all(is_empty(row[col]) for col in ["Asset Class", "Sub-Asset Class", "Instrument/Manager"]):
            return "Classification"
        elif not is_empty(row["Asset Class"]) and all(is_empty(row[col]) for col in ["Sub-Asset Class", "Instrument/Manager"]):
            return "Subheader"
        else:
            return "Normal"

    df["RowType"] = df.apply(classify_row, axis=1)

    # Create a hidden version of the RowType column (used only for styling)
    hidden_rowtype_column = {"field": "RowType", "hide": True}

    gb = GridOptionsBuilder.from_dataframe(df)

    # Inject hidden RowType config manually
    gb.configure_columns(["RowType"], hide=True)

    # Row styling using RowType
    row_style_js = JsCode("""
    function(params) {
        if (params.data.RowType === 'Classification') {
            return {
                'backgroundColor': '#b6e2b6',
                'fontWeight': 'bold',
                'color': 'black'
            };
        } else if (params.data.RowType === 'Subheader') {
            return {
                'backgroundColor': '#eaf8e6'
            };
        }
        return {};
    }
    """)
    gb.configure_grid_options(getRowStyle=row_style_js)

    # Normal numeric config for Allocation columns — no color gradient
    gb.configure_column("Allocation (%)", type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=2)
    gb.configure_column("Allocation ($)", type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=2)

    gridOptions = gb.build()

    AgGrid(
        df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        height=600,
        theme='alpine'
    )





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
            plot_aggrid_table(hierarchical_df)
            
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