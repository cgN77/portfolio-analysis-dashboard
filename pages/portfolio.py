import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import plotly.express as px

def extract_asset_classifications(file_path, sheet_name="Sheet1"):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df.set_index("Name").to_dict(orient="index")

def load_fund_names(file_path="input.xlsx"):
    """Load available Names from database"""
    return pd.read_excel(file_path)["Name"].unique().tolist()

def create_sunburst_table(assets_pct, total_portfolio_value, asset_classifications):
    data = []
    classification_totals = {}

    for asset, alloc_pct in assets_pct.items():
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

def create_summary_table(assets_pct, total_portfolio_value, asset_classifications):
    classification_totals = {}
    
    # First pass - calculate totals and weighted averages
    for asset, alloc_pct in assets_pct.items():
        classification = asset_classifications.get(asset, {}).get("Classification", "Alternative")
        asset_class = asset_classifications.get(asset, {}).get("Asset Class", "")
        sub_asset_class = asset_classifications.get(asset, {}).get("Sub-Asset Class", "")
        public_private = asset_classifications.get(asset, {}).get("Public vs Private", "")
        income_growth = asset_classifications.get(asset, {}).get("Income/Growth", "")
        
        # Get metrics from classifications
        expected_yield = asset_classifications.get(asset, {}).get("Expected Yield (%)", 0)
        expected_return = asset_classifications.get(asset, {}).get("Expected Return (%)", 0)
        expected_volatility = asset_classifications.get(asset, {}).get("Expected Volatility (%)", 0)
        
        allocation_value = (alloc_pct / 100.0) * total_portfolio_value

        # Initialize or update classification totals
        class_group = classification_totals.setdefault(classification, {}).setdefault(asset_class, {}).setdefault(sub_asset_class, {
            "total_pct": 0.0,
            "total_value": 0.0,
            "weighted_yield": 0.0,
            "weighted_return": 0.0,
            "weighted_volatility": 0.0,
            "total_weight": 0.0,
            "yield_contribution": 0.0,
            "return_contribution": 0.0,
            "public_private": public_private,
            "income_growth": income_growth
        })
        
        # Accumulate totals and weighted metrics
        class_group["total_pct"] += alloc_pct
        class_group["total_value"] += allocation_value
        class_group["weighted_yield"] += alloc_pct * expected_yield
        class_group["weighted_return"] += alloc_pct * expected_return
        class_group["weighted_volatility"] += alloc_pct * expected_volatility
        class_group["total_weight"] += alloc_pct
        class_group["yield_contribution"] += (alloc_pct * expected_yield) / 100
        class_group["return_contribution"] += (alloc_pct * expected_return) / 100

    hierarchy_rows = []

    for classification, asset_classes in classification_totals.items():
        classification_alloc_pct = 0
        classification_alloc_dollar = 0
        classification_yield = 0
        classification_return = 0
        classification_volatility = 0
        classification_weight = 0
        classification_yield_contrib = 0
        classification_return_contrib = 0

        # Calculate classification totals
        for asset_class, sub_classes in asset_classes.items():
            for sub_asset_class, totals in sub_classes.items():
                classification_alloc_pct += totals["total_pct"]
                classification_alloc_dollar += totals["total_value"]
                classification_yield += totals["weighted_yield"]
                classification_return += totals["weighted_return"]
                classification_volatility += totals["weighted_volatility"]
                classification_weight += totals["total_weight"]
                classification_yield_contrib += totals["yield_contribution"]
                classification_return_contrib += totals["return_contribution"]

        # Add classification row
        hierarchy_rows.append([
            classification, "", "", "", "",
            round(classification_alloc_pct, 2),
            round(classification_alloc_dollar, 2),
            round(classification_yield/classification_weight, 2) if classification_weight > 0 else 0,
            round((classification_alloc_dollar * (classification_yield/classification_weight/100)) if classification_weight > 0 else 0, 2),
            round(classification_return/classification_weight, 2) if classification_weight > 0 else 0,
            round((classification_alloc_dollar * (classification_return/classification_weight/100)) if classification_weight > 0 else 0, 2),
            round(classification_volatility/classification_weight, 2) if classification_weight > 0 else 0,
            round(classification_yield_contrib, 2),
            round(classification_return_contrib, 2)
        ])

        # Add asset class and sub-asset class rows
        for asset_class, sub_classes in asset_classes.items():
            hierarchy_rows.append(["", asset_class, "", "", "", None, None, None, None, None, None, None, None, None])
            
            for sub_asset_class, totals in sub_classes.items():
                avg_yield = totals["weighted_yield"] / totals["total_weight"] if totals["total_weight"] > 0 else 0
                avg_return = totals["weighted_return"] / totals["total_weight"] if totals["total_weight"] > 0 else 0
                avg_volatility = totals["weighted_volatility"] / totals["total_weight"] if totals["total_weight"] > 0 else 0
                
                hierarchy_rows.append([
                    "", "", sub_asset_class, 
                    totals["public_private"],  # New column
                    totals["income_growth"],   # New column
                    round(totals["total_pct"], 2),
                    round(totals["total_value"], 2),
                    round(avg_yield, 2),
                    round((totals["total_value"] * avg_yield / 100), 2),
                    round(avg_return, 2),
                    round((totals["total_value"] * avg_return / 100), 2),
                    round(avg_volatility, 2),
                    round(totals["yield_contribution"], 2),
                    round(totals["return_contribution"], 2)
                ])

    return pd.DataFrame(hierarchy_rows, columns=[
        "Classification", "Asset Class", "Sub-Asset Class", 
        "Public vs Private", "Income/Growth",  # New columns
        "Total Allocation (%)", "Total Allocation ($)",
        "Expected Yield (%)", "Expected Yield ($)",
        "Expected Return (%)", "Expected Return ($)", 
        "Expected Volatility (%)",
        "Yield Contribution (%)", 
        "Return Contribution (%)"
    ])


# Update the plot_aggrid_table function to handle new columns
def plot_aggrid_table(df):
    def is_empty(val):
        return pd.isna(val) or val == ""

    def classify_row(row):
        # Check if summary table format
        is_summary_table = "Expected Yield (%)" in df.columns
        
        if is_summary_table:
            if not is_empty(row["Classification"]) and is_empty(row["Asset Class"]):
                return "Classification"
            elif not is_empty(row["Asset Class"]) and is_empty(row["Sub-Asset Class"]):
                return "Subheader"
            else:
                return "Normal"
        else:
            # Original detailed table logic
            if not is_empty(row["Classification"]) and all(is_empty(row[col]) for col in ["Asset Class", "Sub-Asset Class", "Instrument/Manager"]):
                return "Classification"
            elif not is_empty(row["Asset Class"]) and all(is_empty(row[col]) for col in ["Sub-Asset Class", "Instrument/Manager"]):
                return "Subheader"
            else:
                return "Normal"

    df["RowType"] = df.apply(classify_row, axis=1)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_columns(["RowType"], hide=True)

    numeric_columns = [
        'Total Allocation (%)', 'Total Allocation ($)',
        'Expected Yield (%)', 'Expected Yield ($)',
        'Expected Return (%)', 'Expected Return ($)', 
        'Expected Volatility (%)',
        'Yield Contribution (%)', 'Return Contribution (%)'
    ]
    
    column_widths = {
        "Classification": 150,
        "Asset Class": 150,
        "Sub-Asset Class": 180,
        "Public vs Private": 120,
        "Income/Growth": 120,
        "Total Allocation (%)": 120,
        "Total Allocation ($)": 140,
        "Expected Yield (%)": 120,
        "Expected Yield ($)": 140,
        "Expected Return (%)": 120,
        "Expected Return ($)": 140,
        "Expected Volatility (%)": 140,
        "Yield Contribution (%)": 150,
        "Return Contribution (%)": 150
    }

    # Configure columns
    for col in df.columns:
        if col in column_widths:
            gb.configure_column(col, width=column_widths[col])
            
        if col in numeric_columns:
            if "$" in col:
                gb.configure_column(col, 
                    type=["numericColumn", "numberColumnFilter"],
                    valueFormatter=JsCode(
                        """function(params) {
                            if (params.value === null) return '';
                            return '$' + params.value.toLocaleString('en-US', 
                                { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                        }"""
                    )
                )
            elif "%" in col:
                gb.configure_column(col,
                    type=["numericColumn", "numberColumnFilter"],
                    valueFormatter=JsCode(
                        """function(params) {
                            if (params.value === null) return '';
                            return params.value.toFixed(2) + '%';
                        }"""
                    )
                )

    row_style_js = JsCode("""
    function(params) {
        if (params.data.RowType === 'Classification') {
            return { backgroundColor: '#b6e2b6', fontWeight: 'bold' };
        } else if (params.data.RowType === 'Subheader') {
            return { backgroundColor: '#eaf8e6' };
        }
        return {};
    }
    """)
    gb.configure_grid_options(getRowStyle=row_style_js)

    gridOptions = gb.build()

    AgGrid(
        df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,  # Disable auto-fit to use our widths
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        height=600,
        theme='alpine'
    )

def create_income_growth_allocation(assets_pct, total_portfolio_value, asset_classifications):
    # Define liquidity mapping to match the desired categories
    liquidity_map = {
        "Liquid": "Liquid",
        "Semi-liquid": "Semi",
        "Illiquid": "Illiquid"
    }
    
    # Initialize the allocation data
    allocation_data = {
        "Cash & Equivalent": {"pct": 0, "value": 0, "sub_assets": {}},
        "Growth (Liquid)": {"pct": 0, "value": 0, "sub_assets": {}},
        "Growth (Semi)": {"pct": 0, "value": 0, "sub_assets": {}},
        "Growth (Illiquid)": {"pct": 0, "value": 0, "sub_assets": {}},
        "Income (Liquid)": {"pct": 0, "value": 0, "sub_assets": {}},
        "Income (Semi)": {"pct": 0, "value": 0, "sub_assets": {}},
        "Income (Illiquid)": {"pct": 0, "value": 0, "sub_assets": {}},
    }
    
    # Process each asset
    for asset, alloc_pct in assets_pct.items():
        # Get asset attributes
        asset_class = asset_classifications.get(asset, {}).get("Asset Class", "")
        sub_asset_class = asset_classifications.get(asset, {}).get("Sub-Asset Class", "")
        income_growth = asset_classifications.get(asset, {}).get("Income/Growth", "")
        liquidity = asset_classifications.get(asset, {}).get("Liquidity", "")
        
        # Calculate allocation value
        allocation_value = (alloc_pct / 100.0) * total_portfolio_value
        
        # Determine category
        if asset_class == "Cash & Equivalent":
            category = "Cash & Equivalent"
        else:
            # Map liquidity to simplified form
            liquidity_key = liquidity_map.get(liquidity, liquidity)
            category = f"{income_growth} ({liquidity_key})"
        
        # Ensure the category exists in our allocation data
        if category not in allocation_data:
            allocation_data[category] = {"pct": 0, "value": 0, "sub_assets": {}}
        
        # Update category totals
        allocation_data[category]["pct"] += alloc_pct
        allocation_data[category]["value"] += allocation_value
        
        # Update sub-asset class within category
        if sub_asset_class not in allocation_data[category]["sub_assets"]:
            allocation_data[category]["sub_assets"][sub_asset_class] = {
                "pct": 0,
                "value": 0
            }
        
        allocation_data[category]["sub_assets"][sub_asset_class]["pct"] += alloc_pct
        allocation_data[category]["sub_assets"][sub_asset_class]["value"] += allocation_value
    
    return allocation_data

def create_income_growth_table(allocation_data):
    rows = []
    
    # Define the desired order of categories
    category_order = [
        "Growth (Liquid)",
        "Growth (Semi)",
        "Growth (Illiquid)",
        "Income (Liquid)",
        "Income (Semi)",
        "Income (Illiquid)",
        "Cash & Equivalent"
    ]
    
    # Add data for each category
    for category in category_order:
        if category in allocation_data:
            data = allocation_data[category]
            
            # Add category header row
            rows.append([category, "", None, None])
            
            # Add sub-asset classes
            for sub_asset, sub_data in data["sub_assets"].items():
                rows.append([
                    "", 
                    sub_asset, 
                    round(sub_data["pct"], 2),
                    round(sub_data["value"], 2)
                ])
    
    # Add total row
    total_pct = sum(data["pct"] for data in allocation_data.values())
    total_value = sum(data["value"] for data in allocation_data.values())
    rows.append(["Total", "", round(total_pct, 2), round(total_value, 2)])
    
    return pd.DataFrame(rows, columns=["Type", "Sub-Asset Class", "Allocation (%)", "Allocation ($)"])

import plotly.graph_objects as go

def plot_income_growth_donut(allocation_data):
    labels = []
    values = []
    colors = []

    # Define colors for each category (match with table)
    color_map = {
        "Growth (Liquid)": "#E6B800",
        "Growth (Semi)": "#F4D06F",
        "Growth (Illiquid)": "#FBE8A6",
        "Income (Liquid)": "#4B4B4B",
        "Income (Semi)": "#B3A580",
        "Income (Illiquid)": "#8C6E63",
        "Cash & Equivalent": "#E2E2E2"
    }

    for category, data in allocation_data.items():
        if data["pct"] > 0:
            labels.append(category)
            values.append(round(data["pct"], 2))
            colors.append(color_map.get(category, "#7f7f7f"))

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='label+percent',
        textposition='inside',
        insidetextorientation='radial'
    )])

    fig.update_layout(
        title_text="Overview on Asset Allocation – Income vs Growth",
        showlegend=False,
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig

def style_income_growth_table(df):
    color_map = {
        "Growth (Liquid)": "#E6B800",
        "Growth (Semi)": "#F4D06F",
        "Growth (Illiquid)": "#FBE8A6",
        "Income (Liquid)": "#4B4B4B",
        "Income (Semi)": "#B3A580",
        "Income (Illiquid)": "#8C6E63",
        "Cash & Equivalent": "#E2E2E2"
    }

    def row_color(row):
        bg_color = color_map.get(row["Type"], "white")
        return [f'background-color: {bg_color}' if row["Sub-Asset Class"] == "" else "" for _ in row]

    styled = df.style.apply(row_color, axis=1)
    styled.format({
        "Allocation (%)": "{:.2f}",
        "Allocation ($)": "${:,.2f}"
    })
    return styled


def main():
    st.set_page_config(page_title="Fund Classification", layout="wide")
    st.title("Portfolio Classification Dashboard")

    available_funds = load_fund_names()
    selected_funds = st.multiselect("Select Funds", available_funds)

    if selected_funds:
        st.subheader("Enter Allocation Amounts ($)")
        allocations = {}

        for fund in selected_funds:
            alloc = st.number_input(
                f"Allocation Amount for {fund}",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                format="%g"
            )
            allocations[fund] = alloc

        total_portfolio_value = sum(allocations.values())

        if total_portfolio_value > 0:
            allocations_pct = {
                fund: (amount / total_portfolio_value) * 100
                for fund, amount in allocations.items()
            }

            asset_classifications = extract_asset_classifications("input.xlsx")

            # Detailed Portfolio Breakdown
            st.subheader("Detailed Portfolio Breakdown")
            hierarchical_df = create_sunburst_table(
                allocations_pct,
                total_portfolio_value,
                asset_classifications
            )
            plot_aggrid_table(hierarchical_df)

            # Summarized View
            st.subheader("Summarized View by Sub-Asset Class")
            summary_df = create_summary_table(
                allocations_pct,
                total_portfolio_value,
                asset_classifications
            )
            plot_aggrid_table(summary_df)

            # Income vs Growth Overview
            st.subheader("Overview on Asset Allocation – Income vs Growth")

            allocation_data = create_income_growth_allocation(
                allocations_pct,
                total_portfolio_value,
                asset_classifications
            )

            # 🟡 Donut chart instead of pie
            donut_chart = plot_income_growth_donut(allocation_data)
            st.plotly_chart(donut_chart, use_container_width=True)

            # 🟢 Income vs Growth Table
            income_growth_table = create_income_growth_table(allocation_data)

            def classify_row(row):
                if row["Type"] and not row["Sub-Asset Class"]:
                    return "Header"
                elif row["Type"] == "Total":
                    return "Total"
                else:
                    return "Normal"

            income_growth_table["RowType"] = income_growth_table.apply(classify_row, axis=1)

            # Build AgGrid
            gb = GridOptionsBuilder.from_dataframe(income_growth_table)
            gb.configure_columns(["RowType"], hide=True)

            gb.configure_column(
                "Allocation (%)",
                type=["numericColumn", "numberColumnFilter"],
                valueFormatter=JsCode(
                    """function(params) {
                        if (params.value === null) return '';
                        return params.value.toFixed(2) + '%';
                    }"""
                )
            )

            gb.configure_column(
                "Allocation ($)",
                type=["numericColumn", "numberColumnFilter"],
                valueFormatter=JsCode(
                    """function(params) {
                        if (params.value === null) return '';
                        return '$' + params.value.toLocaleString('en-US', 
                            { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                    }"""
                )
            )

            # Custom row styling for clarity
            row_style_js = JsCode("""
                function(params) {
                    const type = params.data.Type;
                    const rowType = params.data.RowType;

                    if (rowType === 'Header') {
                        if (type === 'Growth (Liquid)') {
                            return { backgroundColor: '#f1c232', fontWeight: 'bold' };
                        } else if (type === 'Growth (Semi)') {
                            return { backgroundColor: '#ffd966', fontWeight: 'bold' };
                        } else if (type === 'Growth (Illiquid)') {
                            return { backgroundColor: '#fff2cc', fontWeight: 'bold' };
                        } else if (type === 'Income (Liquid)') {
                            return { backgroundColor: '#434343', color: 'white', fontWeight: 'bold' };
                        } else if (type === 'Income (Semi)') {
                            return { backgroundColor: '#999999', color: 'white', fontWeight: 'bold' };
                        } else if (type === 'Income (Illiquid)') {
                            return { backgroundColor: '#d9d9d9', fontWeight: 'bold' };
                        } else if (type === 'Cash & Equivalent') {
                            return { backgroundColor: '#eeeeee', fontWeight: 'bold' };
                        }
                    }

                    if (rowType === 'Total') {
                        return { backgroundColor: '#f9f9f9', fontWeight: 'bold' };
                    }

                    return {};
                }
                """)

            gb.configure_grid_options(getRowStyle=row_style_js)

            gridOptions = gb.build()

            AgGrid(
                income_growth_table,
                gridOptions=gridOptions,
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=False,
                allow_unsafe_jscode=True,
                height=400,
                theme='alpine'
            )

            # ⬇ Download Report
            csv = pd.concat([hierarchical_df, summary_df, income_growth_table.drop(columns=["RowType"])]).to_csv(index=False)
            st.download_button(
                "Download Full Report (CSV)",
                data=csv,
                file_name="portfolio_breakdown.csv",
                mime="text/csv"
            )
        else:
            st.warning("Total allocation amount must be greater than $0")
    else:
        st.info("Please select funds to begin portfolio construction")


if __name__ == "__main__":
    main()