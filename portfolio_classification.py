import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.table import Table

def extract_asset_classifications(file_path, sheet_name="Sheet1"):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    asset_classifications = {
        row["Asset"]: {
            "Classification": row["Classification"],
            "Asset Class": row["Asset Class"],
            "Sub-Asset Class": row["Sub-Asset Class"],
            "Liquidity": row["Liquidity"],
            "Instrument/Manager": row["Instrument/Manager"],
        }
        for _, row in df.iterrows()
    }
    return asset_classifications

def create_sunburst_table(assets, total_portfolio_value, asset_classifications):
    data = []
    for asset, alloc_pct in assets.items():
        classification = asset_classifications.get(asset, {})
        data.append({
            "Classification": classification.get("Classification", "Alternative"),
            "Asset Class": classification.get("Asset Class", ""),
            "Sub-Asset Class": classification.get("Sub-Asset Class", ""),
            "Liquidity": classification.get("Liquidity", "Illiquid"),
            "Instrument/Manager": classification.get("Instrument/Manager", asset),
            "Allocation (%)": alloc_pct,
            "Allocation ($)": (alloc_pct / 100.0) * total_portfolio_value,
        })
    df = pd.DataFrame(data)
    return df

def plot_sunburst_table(df):
    fig, ax = plt.subplots(figsize=(10, len(df) * 0.5))
    ax.set_frame_on(False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    
    table = Table(ax, bbox=[0, 0, 1, 1])
    col_labels = list(df.columns)
    cell_colors = [['#4f81bd' if i == 0 else '#dbe5f1' for i in range(len(col_labels))]]
    
    # Add headers
    for j, label in enumerate(col_labels):
        table.add_cell(0, j, width=1/len(col_labels), height=0.2, text=label, loc='center', facecolor='#4f81bd', edgecolor='black', fontsize=10, fontweight='bold', text_props={'color': 'white'})
    
    # Add data
    for i, row in enumerate(df.itertuples(), start=1):
        for j, value in enumerate(row[1:]):
            table.add_cell(i, j, width=1/len(col_labels), height=0.15, text=str(value), loc='center', facecolor='#dbe5f1' if i % 2 == 0 else 'white', edgecolor='black', fontsize=9)
    
    ax.add_table(table)
    plt.show()