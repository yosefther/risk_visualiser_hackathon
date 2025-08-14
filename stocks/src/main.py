from python_units.stock_downloader import StockDataDownloader, download_portfolio_data, quick_download

def get_user_portfolio_data():
    """Get portfolio data based on user input"""
    # Initialize downloader
    downloader = StockDataDownloader("my_portfolio_data")
    
    # Get user input
    user_tickers = input("Enter stock tickers (space or comma separated): ").strip()
    tickers = user_tickers.replace(',', ' ').split()
    
    # Download data
    results = downloader.download_multiple_tickers(tickers)
    
    # Load data for analysis/plotting
    successful_tickers = [ticker for ticker, success in results.items() if success]
    
    portfolio_data = {}
    for ticker in successful_tickers:
        data = downloader.load_ticker_data(ticker)
        if data is not None:
            portfolio_data[ticker] = data
            print(f"{ticker}: {len(data)} data points from {data.index[0]} to {data.index[-1]}")
    
    return portfolio_data

def get_portfolio_data(ticker_list):
    """Get data ready for Plotly visualization (for predefined tickers)"""
    downloader = StockDataDownloader("my_portfolio_data")
    
    # Download if not already downloaded
    results = downloader.download_multiple_tickers(ticker_list)
    
    # Load all successful downloads
    portfolio_data = {}
    for ticker, success in results.items():
        if success:
            data = downloader.load_ticker_data(ticker)
            if data is not None:
                portfolio_data[ticker] = data
    
    return portfolio_data

if __name__ == "__main__":
    # Get portfolio data from user input
    portfolio_data = get_user_portfolio_data()
    
    # Now you can use portfolio_data for further processing
    print(f"\nSuccessfully loaded data for {len(portfolio_data)} stocks:")
    for ticker, df in portfolio_data.items():
        print(f"{ticker}: {len(df)} records, latest close: ${df['Close'][-1]:.2f}")
    
    # Here you could pass portfolio_data to your Plotly visualization functions

