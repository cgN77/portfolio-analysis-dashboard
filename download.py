import yfinance as yf
import pandas as pd
# Define the stock ticker
tickers = ["KEI.NS","OLAELEC.NS","TITAN.NS","TRENT.NS","POLYCAB.NS","INTELLECT.NS","IDEA.NS"]

start_date = "2019-03-29"
end_date = "2024-03-29"

# Loop through each stock and download data
date_format = "%m/%d/%y"

# Loop through each stock
for ticker in tickers:
    # Download historical data
    stock_data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)

    # Select required columns: Date, Close Price, Dividends
    stock_data = stock_data[['Close']].copy()

    # Resample to get only month-end data
    stock_data = stock_data.resample('M').last()

    # Calculate monthly returns
    stock_data['Returns'] = stock_data['Close'].pct_change()

    # Reset index to have 'Date' as a column and format it
    stock_data.reset_index(inplace=True)
    stock_data.rename(columns={'Date': 'time', 'Close': 'price'}, inplace=True)
    stock_data['time'] = stock_data['time'].dt.strftime(date_format)

    # Save to CSV file named after the stock
    filename = f"{ticker.replace('.NS', '')}_stock_data.csv"
    stock_data.to_csv(filename, index=False)
    
    print(f"File saved: {filename}")


