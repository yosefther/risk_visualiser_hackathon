import yfinance as yf
import pandas as pd
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

class StockDataDownloader:
    """
    A class to download and save stock data from Yahoo Finance.
    Focuses on maximum available historical data for portfolio analysis.
    """
    
    def __init__(self, data_directory: str = "stock_data"):
        """
        Initialize the downloader with a specified data directory.
        
        Args:
            data_directory (str): Directory to save CSV files
        """
        self.data_directory = data_directory
        self._create_directory()
        
    def _create_directory(self) -> None:
        """Create the data directory if it doesn't exist."""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            print(f"Created directory: {self.data_directory}")
    
    def validate_tickers(self, tickers: List[str]) -> Dict[str, bool]:
        """
        Validate if tickers exist and have data available.
        
        Args:
            tickers (List[str]): List of ticker symbols
            
        Returns:
            Dict[str, bool]: Dictionary mapping ticker to validity status
        """
        validation_results = {}
        print("Validating tickers...")
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker.upper())
                info = stock.info
                # Check if we got valid info (empty dict means invalid ticker)
                is_valid = bool(info and 'symbol' in info)
                validation_results[ticker.upper()] = is_valid
                status = "✓" if is_valid else "✗"
                print(f"{status} {ticker.upper()}")
            except Exception as e:
                validation_results[ticker.upper()] = False
                print(f"✗ {ticker.upper()} - Error: {str(e)}")
                
        return validation_results
    
    def download_single_ticker(self, ticker: str, save_info: bool = False) -> bool:
        """
        Download comprehensive data for a single ticker including historical data,
        financials, and other available datasets. Creates a subfolder for each ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            save_info (bool): Whether to save company info as JSON (default: False)
            
        Returns:
            bool: Success status
        """
        ticker = ticker.upper()
        files_created = []
        
        # Create ticker-specific subfolder
        ticker_directory = os.path.join(self.data_directory, ticker)
        if not os.path.exists(ticker_directory):
            os.makedirs(ticker_directory)
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get maximum historical data (main requirement)
            hist_data = stock.history(period="max")
            
            if hist_data.empty:
                print(f"✗ {ticker}: No historical data available")
                return False
            
            # Save historical data
            hist_filename = os.path.join(ticker_directory, "historical.csv")
            hist_data.to_csv(hist_filename)
            files_created.append("historical")
            
            # Get and save quarterly financials
            try:
                quarterly_income = stock.quarterly_income_stmt
                if not quarterly_income.empty:
                    quarterly_filename = os.path.join(ticker_directory, "quarterly_income.csv")
                    quarterly_income.to_csv(quarterly_filename)
                    files_created.append("quarterly_income")
            except Exception:
                pass  # Skip if not available
            
            # Get and save quarterly balance sheet
            try:
                quarterly_balance = stock.quarterly_balance_sheet
                if not quarterly_balance.empty:
                    balance_filename = os.path.join(ticker_directory, "quarterly_balance_sheet.csv")
                    quarterly_balance.to_csv(balance_filename)
                    files_created.append("quarterly_balance")
            except Exception:
                pass
            
            # Get and save quarterly cash flow
            try:
                quarterly_cashflow = stock.quarterly_cashflow
                if not quarterly_cashflow.empty:
                    cashflow_filename = os.path.join(ticker_directory, "quarterly_cashflow.csv")
                    quarterly_cashflow.to_csv(cashflow_filename)
                    files_created.append("quarterly_cashflow")
            except Exception:
                pass
            
            # Get and save annual financials
            try:
                annual_income = stock.income_stmt
                if not annual_income.empty:
                    annual_filename = os.path.join(ticker_directory, "annual_income.csv")
                    annual_income.to_csv(annual_filename)
                    files_created.append("annual_income")
            except Exception:
                pass
            
            # Get and save annual balance sheet
            try:
                annual_balance = stock.balance_sheet
                if not annual_balance.empty:
                    annual_balance_filename = os.path.join(ticker_directory, "annual_balance_sheet.csv")
                    annual_balance.to_csv(annual_balance_filename)
                    files_created.append("annual_balance")
            except Exception:
                pass
            
            # Get and save annual cash flow
            try:
                annual_cashflow = stock.cashflow
                if not annual_cashflow.empty:
                    annual_cashflow_filename = os.path.join(ticker_directory, "annual_cashflow.csv")
                    annual_cashflow.to_csv(annual_cashflow_filename)
                    files_created.append("annual_cashflow")
            except Exception:
                pass
            
            # Get and save dividends data
            try:
                dividends = stock.dividends
                if not dividends.empty:
                    dividends_filename = os.path.join(ticker_directory, "dividends.csv")
                    dividends.to_csv(dividends_filename)
                    files_created.append("dividends")
            except Exception:
                pass
            
            # Get and save stock splits data
            try:
                splits = stock.splits
                if not splits.empty:
                    splits_filename = os.path.join(ticker_directory, "splits.csv")
                    splits.to_csv(splits_filename)
                    files_created.append("splits")
            except Exception:
                pass
            
            # Save company info if requested (disabled by default)
            if save_info:
                try:
                    info = stock.info
                    if info:
                        info_filename = os.path.join(ticker_directory, "info.json")
                        with open(info_filename, 'w') as f:
                            json.dump(info, f, indent=2, default=str)
                        files_created.append("info")
                except Exception as e:
                    print(f"Warning: Could not save info for {ticker}: {str(e)}")
            
            # Get date range info
            start_date = hist_data.index[0].strftime('%Y-%m-%d')
            end_date = hist_data.index[-1].strftime('%Y-%m-%d')
            
            print(f"✓ {ticker}: {len(hist_data)} records ({start_date} to {end_date}) - Files: {', '.join(files_created)}")
            return True
            
        except Exception as e:
            print(f"✗ {ticker}: Error downloading - {str(e)}")
            return False
    
    def download_multiple_tickers(self, tickers: List[str], validate_first: bool = True, 
                                 delay_seconds: float = 0.5) -> Dict[str, bool]:
        """
        Download data for multiple tickers.
        
        Args:
            tickers (List[str]): List of ticker symbols
            validate_first (bool): Validate tickers before downloading
            delay_seconds (float): Delay between downloads to avoid rate limiting
            
        Returns:
            Dict[str, bool]: Dictionary mapping ticker to success status
        """
        # Clean and uppercase tickers
        tickers = [ticker.upper().strip() for ticker in tickers]
        tickers = list(set(tickers))  # Remove duplicates
        
        print(f"Starting download for {len(tickers)} tickers...")
        
        # Validate tickers if requested
        if validate_first:
            validation_results = self.validate_tickers(tickers)
            valid_tickers = [t for t, valid in validation_results.items() if valid]
            invalid_count = len(tickers) - len(valid_tickers)
            
            if invalid_count > 0:
                print(f"Skipping {invalid_count} invalid ticker(s)")
            
            tickers = valid_tickers
        
        if not tickers:
            print("No valid tickers to download")
            return {}
        
        print(f"\nDownloading data for {len(tickers)} valid ticker(s)...")
        
        # Download each ticker
        results = {}
        for i, ticker in enumerate(tickers, 1):
            print(f"[{i}/{len(tickers)}] Downloading {ticker}...")
            results[ticker] = self.download_single_ticker(ticker)
            
            # Add delay to avoid rate limiting (except for last ticker)
            if i < len(tickers) and delay_seconds > 0:
                time.sleep(delay_seconds)
        
        # Summary
        successful = sum(results.values())
        print(f"\nDownload complete: {successful}/{len(tickers)} successful")
        
        return results
    
    def bulk_download(self, tickers: List[str]) -> Optional[pd.DataFrame]:
        """
        Download multiple tickers in a single API call (more efficient).
        Note: This method doesn't save individual CSV files.
        
        Args:
            tickers (List[str]): List of ticker symbols
            
        Returns:
            pd.DataFrame: Combined data for all tickers
        """
        tickers = [ticker.upper().strip() for ticker in tickers]
        tickers = list(set(tickers))  # Remove duplicates
        
        try:
            print(f"Bulk downloading {len(tickers)} tickers...")
            data = yf.download(tickers, period='max', group_by='ticker', 
                             progress=True, show_errors=True)
            
            if data.empty:
                print("No data retrieved")
                return None
            
            # Save combined data
            filename = os.path.join(self.data_directory, "bulk_download.csv")
            data.to_csv(filename)
            print(f"Bulk data saved to {filename}")
            
            return data
            
        except Exception as e:
            print(f"Bulk download failed: {str(e)}")
            return None
    
    def get_available_files(self) -> List[str]:
        """Get list of downloaded CSV files."""
        if not os.path.exists(self.data_directory):
            return []
        
        return [f for f in os.listdir(self.data_directory) if f.endswith('.csv')]
    
    def load_ticker_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Load historical data for a ticker from saved CSV in its subfolder.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            pd.DataFrame: Historical stock data
        """
        ticker = ticker.upper()
        filename = os.path.join(self.data_directory, ticker, "historical.csv")
        
        if not os.path.exists(filename):
            print(f"No historical data file found for {ticker}")
            return None
        
        try:
            data = pd.read_csv(filename, index_col=0, parse_dates=True)
            return data
        except Exception as e:
            print(f"Error loading data for {ticker}: {str(e)}")
            return None

# Example usage functions
def download_portfolio_data(tickers: List[str], data_dir: str = "stock_data") -> Dict[str, bool]:
    """
    Convenience function to download data for a portfolio of stocks.
    
    Args:
        tickers (List[str]): List of ticker symbols
        data_dir (str): Directory to save data
        
    Returns:
        Dict[str, bool]: Download success status for each ticker
    """
    downloader = StockDataDownloader(data_dir)
    return downloader.download_multiple_tickers(tickers)

def quick_download(ticker_string: str, data_dir: str = "stock_data") -> Dict[str, bool]:
    """
    Quick download from a space or comma-separated string of tickers.
    
    Args:
        ticker_string (str): Space or comma-separated ticker symbols
        data_dir (str): Directory to save data
        
    Returns:
        Dict[str, bool]: Download success status for each ticker
    """
    # Parse ticker string
    tickers = ticker_string.replace(',', ' ').split()
    return download_portfolio_data(tickers, data_dir)

