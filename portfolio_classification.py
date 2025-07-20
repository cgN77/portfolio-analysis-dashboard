import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple

# Define the classification mapping based on the dataset (for pie charts and tables)
ASSET_CLASSIFICATIONS = {
    'US Stock ETF': ('Traditional', 'Public', 'Highly Liquid'),
    'Corporate Bond Fund': ('Traditional', 'Public', 'Highly Liquid'),
    'Private Equity Fund': ('Alternative', 'Private', 'Illiquid'),
    'Real Estate Investment': ('Alternative', 'Private', 'Moderately Liquid'),
    'Hedge Fund': ('Alternative', 'Private', 'Moderately Liquid'),
    'Cryptocurrency': ('Alternative', 'Public', 'Highly Liquid'),
    'Treasury Bond ETF': ('Traditional', 'Public', 'Highly Liquid'),
    'Venture Capital Fund': ('Alternative', 'Private', 'Illiquid'),
    'Art Collection': ('Alternative', 'Private', 'Illiquid'),
    'Infrastructure Fund': ('Alternative', 'Private', 'Illiquid')
}

# Define the hierarchical mapping for the sunburst chart (based on the image)
ASSET_HIERARCHY = {
    # Traditional Assets
    'US Stock ETF': {'category': 'Traditional', 'subcategory': 'Public Equity'},
    'Corporate Bond Fund': {'category': 'Traditional', 'subcategory': 'Fixed Income'},
    'Treasury Bond ETF': {'category': 'Traditional', 'subcategory': 'Fixed Income'},
    # Adding some assets from the image to demonstrate the full hierarchy
    'Bellator': {'category': 'Traditional', 'subcategory': 'Public Equity'},
    'US Tech (Glynn)': {'category': 'Traditional', 'subcategory': 'Public Equity'},
    'Katam Hill (Global)': {'category': 'Traditional', 'subcategory': 'Public Equity'},
    'Quantix': {'category': 'Traditional', 'subcategory': 'Commodities'},
    'Money Market Funds': {'category': 'Traditional', 'subcategory': 'Cash & Equivalent'},
    'Osterweis': {'category': 'Traditional', 'subcategory': 'Fixed Income'},
    'Artisan Partners': {'category': 'Traditional', 'subcategory': 'Fixed Income'},
    'Bramshill': {'category': 'Traditional', 'subcategory': 'Fixed Income'},

    # Alternative Assets
    'Private Equity Fund': {'category': 'Alternative', 'subcategory': 'Private Equity'},
    'Real Estate Investment': {'category': 'Alternative', 'subcategory': 'Real Assets'},
    'Hedge Fund': {'category': 'Alternative', 'subcategory': 'Hedge Funds'},
    'Cryptocurrency': {'category': 'Alternative', 'subcategory': 'Digital Assets'},
    'Venture Capital Fund': {'category': 'Alternative', 'subcategory': 'Private Equity'},
    'Art Collection': {'category': 'Alternative', 'subcategory': 'Real Assets'},
    'Infrastructure Fund': {'category': 'Alternative', 'subcategory': 'Real Assets'},
    # Adding some assets from the image to demonstrate the full hierarchy
    'Monroe': {'category': 'Alternative', 'subcategory': 'Private Credit'},
    'Callodine': {'category': 'Alternative', 'subcategory': 'Private Credit'},
    'ASP': {'category': 'Alternative', 'subcategory': 'Private Credit'},
    'Regan': {'category': 'Alternative', 'subcategory': 'Private Credit'},
    'Origin': {'category': 'Alternative', 'subcategory': 'Private Credit'},
    'Katam Hill (Hedge)': {'category': 'Alternative', 'subcategory': 'Hedge Funds'},
    'NIM': {'category': 'Alternative', 'subcategory': 'Hedge Funds'},
    'Evergreen (Secondaries, Co-Invest)': {'category': 'Alternative', 'subcategory': 'Private Equity'},
    'HarbourVest': {'category': 'Alternative', 'subcategory': 'Private Equity'},
}

def classify_asset(asset_name: str) -> Tuple[str, str, str]:
    """
    Classify an asset based on the predefined classifications.
    Returns (traditional/alternative, public/private, liquidity level)
    """
    # Check if asset is in our classification mapping
    if asset_name in ASSET_CLASSIFICATIONS:
        return ASSET_CLASSIFICATIONS[asset_name]
    
    # Default classification for unknown assets
    return ('Alternative', 'Private', 'Illiquid')

def create_styled_table(df):
    """Create a styled HTML table for classification data"""
    
    # Define CSS styles
    table_style = """
    <style>
        .classification-table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-family: Arial, sans-serif;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .classification-table th {
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        .classification-table td {
            padding: 12px;
            border: 1px solid #ddd;
        }
        .classification-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .classification-table tr:hover {
            background-color: #f2f2f2;
        }
        .traditional-text {
            color: #d49811; /* Gold */
            font-weight: bold;
        }
        .alternative-text {
            color: #283747; /* Dark Blue */
            font-weight: bold;
        }
        .public {
            background-color: rgba(92, 184, 219, 0.1); /* Light Blue */
        }
        .private {
            background-color: rgba(144, 201, 126, 0.1); /* Light Green */
        }
        .highly-liquid {
            color: #27ae60;
        }
        .moderately-liquid {
            color: #f39c12;
        }
        .illiquid {
            color: #c0392b;
        }
    </style>
    """
    
    # Create HTML table
    html_content = f"{table_style}<table class=\'classification-table\'>"
    
    # Add headers
    html_content += "<tr>"
    for col in df.columns:
        html_content += f"<th>{col}</th>"
    html_content += "</tr>"
    
    # Add rows with styling
    for _, row in df.iterrows():
        html_content += "<tr>"
        
        # Asset Name
        html_content += f"<td>{row['Asset Type']}</td>"
        
        # Category with color coding
        category_class = 'traditional-text' if row['Category'] == 'Traditional' else 'alternative-text'
        html_content += f"<td class='{category_class}'>{row['Category']}</td>"
        
        # Access with background color
        access_class = 'public' if row['Access'] == 'Public' else 'private'
        html_content += f"<td class='{access_class}'>{row['Access']}</td>"
        
        # Liquidity with color coding
        liquidity_class = ''
        if row['Liquidity'] == 'Highly Liquid':
            liquidity_class = 'highly-liquid'
        elif row['Liquidity'] == 'Moderately Liquid':
            liquidity_class = 'moderately-liquid'
        else:
            liquidity_class = 'illiquid'
        html_content += f"<td class='{liquidity_class}'>{row['Liquidity']}</td>"
        
        html_content += "</tr>"
    
    html_content += "</table>"
    return html_content

def create_sunburst_chart(assets: Dict[str, float]):
    """Create a sunburst chart for portfolio hierarchy"""
    chart_data = []
    for asset_name, allocation in assets.items():
        if asset_name in ASSET_HIERARCHY:
            hierarchy_info = ASSET_HIERARCHY[asset_name]
            chart_data.append({
                'ids': asset_name,
                'labels': asset_name,
                'parents': hierarchy_info['subcategory'],
                'values': allocation
            })
            # Add subcategory if not already present
            if hierarchy_info['subcategory'] not in [d['ids'] for d in chart_data]:
                chart_data.append({
                    'ids': hierarchy_info['subcategory'],
                    'labels': hierarchy_info['subcategory'],
                    'parents': hierarchy_info['category'],
                    'values': allocation # This value will be summed up by Plotly
                })
            # Add category if not already present
            if hierarchy_info['category'] not in [d['ids'] for d in chart_data]:
                chart_data.append({
                    'ids': hierarchy_info['category'],
                    'labels': hierarchy_info['category'],
                    'parents': '', # Top level has no parent
                    'values': allocation # This value will be summed up by Plotly
                })

    # Convert to DataFrame for Plotly
    df_sunburst = pd.DataFrame(chart_data)

    # Manually aggregate values for parents
    # This is important for correct sizing of higher-level segments
    aggregated_data = {}

    # Aggregate for assets and subcategories
    for asset_name, allocation in assets.items():
        if asset_name in ASSET_HIERARCHY:
            hierarchy_info = ASSET_HIERARCHY[asset_name]
            # Add asset allocation
            if asset_name not in aggregated_data: # Ensure asset itself is in there for values
                aggregated_data[asset_name] = {'labels': asset_name, 'parents': hierarchy_info['subcategory'], 'values': 0}
            aggregated_data[asset_name]['values'] += allocation

            # Aggregate subcategory allocation
            if hierarchy_info['subcategory'] not in aggregated_data:
                aggregated_data[hierarchy_info['subcategory']] = {'labels': hierarchy_info['subcategory'], 'parents': hierarchy_info['category'], 'values': 0}
            aggregated_data[hierarchy_info['subcategory']]['values'] += allocation
            
            # Aggregate category allocation
            if hierarchy_info['category'] not in aggregated_data:
                aggregated_data[hierarchy_info['category']] = {'labels': hierarchy_info['category'], 'parents': '', 'values': 0}
            aggregated_data[hierarchy_info['category']]['values'] += allocation

    # Convert the aggregated data to a DataFrame
    sunburst_final_df = pd.DataFrame.from_dict(aggregated_data, orient='index')
    # Reset index to make 'ids' column from keys
    sunburst_final_df['ids'] = sunburst_final_df.index
    sunburst_final_df = sunburst_final_df.reset_index(drop=True)

    # Define colors similar to the image
    # Inner ring colors
    color_discrete_map_outer = {
        'Traditional': '#d49811',  # Gold for Traditional
        'Alternative': '#283747'   # Dark Blue for Alternative
    }

    # Assign colors to subcategories based on their parent category
    # This is a bit tricky with px.sunburst. We can use `color` argument and `color_discrete_map`
    # to control colors for different levels. For more granular control as in the image,
    # we might need to use go.Sunburst or define a very specific color_discrete_map
    # for all labels or rely on Plotly's default sequencing for inner rings if not explicitly mapped.
    
    # For this implementation, I will assign color based on the immediate parent category for the middle ring,
    # and let Plotly handle the outermost ring (specific assets) with its default sequencing or a generic map.

    # Creating a DataFrame that includes the top-level categories for coloring
    sunburst_final_df['top_category'] = sunburst_final_df['ids'].apply(lambda x: ASSET_HIERARCHY[x]['category'] if x in ASSET_HIERARCHY else x)

    fig = px.sunburst(sunburst_final_df,
                      path=['top_category', 'parents', 'labels'], # The order defines the hierarchy
                      values='values',
                      color='top_category',
                      color_discrete_map=color_discrete_map_outer,
                      title="Portfolio Hierarchical Breakdown",
                      branchvalues='total') # Ensures parent values represent sum of children

    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    fig.update_traces(hovertemplate='<b>%{label}</b><br>Allocation: %{value:.1f}%')

    return fig

def create_classification_charts(assets: Dict[str, float]):
    """Create classification charts based on asset data"""
    # Prepare data
    df = pd.DataFrame([
        {
            'Asset': name,
            'Allocation': value,
            'Type': classify_asset(name)[0],
            'Access': classify_asset(name)[1],
            'Liquidity': classify_asset(name)[2]
        }
        for name, value in assets.items()
    ])

    # Create pie charts with consistent colors
    # Colors adjusted to be more in line with the sunburst chart's general theme
    color_map = {
        'Traditional': '#d49811', # Gold
        'Alternative': '#283747', # Dark Blue
        'Public': '#5cb8db', # Light Blue
        'Private': '#90c97e', # Light Green
        'Highly Liquid': '#27ae60',
        'Moderately Liquid': '#f39c12',
        'Illiquid': '#c0392b'
    }

    fig_type = px.pie(
        df, 
        values='Allocation', 
        names='Type',
        title='Portfolio Distribution: Traditional vs Alternative',
        color_discrete_map={'Traditional': color_map['Traditional'], 
                          'Alternative': color_map['Alternative']}
    )
    
    fig_access = px.pie(
        df, 
        values='Allocation', 
        names='Access',
        title='Portfolio Distribution: Public vs Private',
        color_discrete_map={'Public': color_map['Public'], 
                          'Private': color_map['Private']}
    )
    
    fig_liquidity = px.pie(
        df, 
        values='Allocation', 
        names='Liquidity',
        title='Portfolio Distribution by Liquidity',
        color_discrete_map={
            'Highly Liquid': color_map['Highly Liquid'],
            'Moderately Liquid': color_map['Moderately Liquid'],
            'Illiquid': color_map['Illiquid']
        }
    )

    # Create summary table
    summary_df = pd.DataFrame([
        df.groupby('Type')['Allocation'].sum(),
        df.groupby('Access')['Allocation'].sum(),
        df.groupby('Liquidity')['Allocation'].sum()
    ], index=['By Type', 'By Access', 'By Liquidity'])

    # Create detailed classification table
    classification_df = pd.DataFrame([
        {
            'Asset Type': name,
            'Category': classify_asset(name)[0],
            'Access': classify_asset(name)[1],
            'Liquidity': classify_asset(name)[2]
        }
        for name in assets.keys()
    ])

    return fig_type, fig_access, fig_liquidity, summary_df, classification_df

def main():
    st.title("Portfolio Classification Analysis")
    
    st.write("""
    This tool helps you analyze your portfolio composition based on:
    - Traditional vs Alternative assets
    - Public vs Private markets
    - Liquidity levels
    """)

    # Display classification table
    st.subheader("Asset Classification Reference")
    classification_data = pd.DataFrame([
        {
            'Asset Type': asset,
            'Category': cat,
            'Access': acc,
            'Liquidity': liq
        }
        for asset, (cat, acc, liq) in ASSET_CLASSIFICATIONS.items()
    ])
    
    # Display the styled table
    st.markdown(create_styled_table(classification_data), unsafe_allow_html=True)

    # Initialize session state for assets if it doesn't exist
    if 'assets' not in st.session_state:
        st.session_state.assets = {}

    # Input form
    with st.form("asset_input_form"):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.selectbox(
                "Asset Name",
                options=list(ASSET_HIERARCHY.keys()), # Use ASSET_HIERARCHY keys for broader selection
                help="Select an asset from the predefined list"
            )
        with col2:
            allocation = st.number_input("Allocation (%)", min_value=0.0, max_value=100.0, value=0.0)
        
        submitted = st.form_submit_button("Add Asset")
        if submitted and asset_name and allocation:
            st.session_state.assets[asset_name] = allocation

    # Display current assets
    if st.session_state.assets:
        st.subheader("Current Portfolio")
        portfolio_df = pd.DataFrame([
            {"Asset": k, "Allocation (%)": v} 
            for k, v in st.session_state.assets.items()
        ])
        st.dataframe(portfolio_df)

        # Add option to remove assets
        asset_to_remove = st.selectbox(
            "Select asset to remove",
            ["None"] + list(st.session_state.assets.keys())
        )
        if asset_to_remove != "None" and st.button("Remove Selected Asset"):
            del st.session_state.assets[asset_to_remove]
            st.experimental_rerun()

        # Create and display charts
        total_allocation = sum(st.session_state.assets.values())
        if abs(total_allocation - 100) > 0.01:  # Allow for small floating-point differences
            st.warning(f"Total allocation ({total_allocation}%) does not equal 100%")
        
        # Create pie charts
        fig_type, fig_access, fig_liquidity, summary_df, classification_df = create_classification_charts(st.session_state.assets)

        # Create sunburst chart
        sunburst_fig = create_sunburst_chart(st.session_state.assets)

        # Display charts in columns
        st.subheader("Portfolio Composition Visualizations")
        st.plotly_chart(sunburst_fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_type, use_container_width=True)
            st.plotly_chart(fig_liquidity, use_container_width=True)
        with col2:
            st.plotly_chart(fig_access, use_container_width=True)

        # Display summary statistics
        st.subheader("Portfolio Classification Summary (%)")
        st.dataframe(summary_df)

        # Display detailed classification with styling
        st.subheader("Detailed Asset Classification")
        st.markdown(create_styled_table(classification_df), unsafe_allow_html=True)

        # Add download button for the data
        csv = classification_df.to_csv(index=False)
        st.download_button(
            label="Download Portfolio Classification Data",
            data=csv,
            file_name="portfolio_classification.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()