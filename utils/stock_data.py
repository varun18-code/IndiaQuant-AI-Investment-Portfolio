import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_stock_data(ticker, period='1y', interval='1d', real_time=False):
    """
    Fetch stock data using yfinance with real-time option
    
    Parameters:
    ticker (str): Stock ticker symbol
    period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    real_time (bool): If True, attempts to get real-time intraday data
    
    Returns:
    pd.DataFrame: DataFrame with stock data
    """
    try:
        stock = yf.Ticker(ticker)
        
        # For real-time data, use the smallest available interval for intraday analysis
        if real_time and interval not in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
            interval = '5m'  # Use 5-minute intervals for real-time data
            period = '1d'    # Last day for real-time analysis
        
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            return None
            
        # Normalize timestamp indices to avoid timezone comparison issues
        if df.index.tzinfo is not None:
            df.index = df.index.tz_localize(None)
        
        # Add trading session information for Indian markets
        if not df.empty:
            # India Standard Time (IST) is UTC+5:30 (create a copy with timezone to avoid modifying the index)
            df['IST_Time'] = pd.Series(df.index, index=df.index) + pd.Timedelta(hours=5, minutes=30)
            
            # Check if the data point is during Indian trading hours (9:15 AM to 3:30 PM IST)
            df['Trading_Session'] = df['IST_Time'].apply(
                lambda x: 'Regular' if (
                    (x.hour > 9 or (x.hour == 9 and x.minute >= 15)) and 
                    (x.hour < 15 or (x.hour == 15 and x.minute <= 30))
                ) else 'Extended'
            )
        
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def get_stock_info(ticker):
    """
    Fetch stock information
    
    Parameters:
    ticker (str): Stock ticker symbol
    
    Returns:
    dict: Dictionary with stock information
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract key information
        stock_info = {
            'shortName': info.get('shortName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'marketCap': info.get('marketCap', 0),
            'forwardPE': info.get('forwardPE', 0),
            'dividendYield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 0),
            'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', 0),
            'website': info.get('website', 'N/A'),
            'longBusinessSummary': info.get('longBusinessSummary', 'N/A')
        }
        
        return stock_info
    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return {
            'shortName': ticker,
            'sector': 'Error',
            'industry': 'Error',
            'marketCap': 0,
            'forwardPE': 0,
            'dividendYield': 0,
            'fiftyTwoWeekHigh': 0,
            'fiftyTwoWeekLow': 0,
            'website': 'N/A',
            'longBusinessSummary': f"Error fetching data: {e}"
        }

def get_multiple_stocks_data(tickers, period='1y', interval='1d'):
    """
    Fetch data for multiple stocks
    
    Parameters:
    tickers (list): List of stock ticker symbols
    period (str): Data period
    interval (str): Data interval
    
    Returns:
    dict: Dictionary with stock data for each ticker
    """
    data = {}
    for ticker in tickers:
        data[ticker] = get_stock_data(ticker, period, interval)
    return data

def calculate_stock_returns(data):
    """
    Calculate daily and cumulative returns for stock data
    
    Parameters:
    data (pd.DataFrame): DataFrame with stock data
    
    Returns:
    pd.DataFrame: DataFrame with daily and cumulative returns added
    """
    if data is None or data.empty:
        return None
        
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    # Calculate daily returns
    df['Daily_Return'] = df['Close'].pct_change()
    
    # Calculate cumulative returns
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
    
    return df

def calculate_volatility(data, window=20):
    """
    Calculate rolling volatility for stock data
    
    Parameters:
    data (pd.DataFrame): DataFrame with stock data
    window (int): Rolling window size
    
    Returns:
    pd.DataFrame: DataFrame with volatility added
    """
    if data is None or data.empty:
        return None
        
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    # Calculate rolling volatility (standard deviation of returns)
    df['Volatility'] = df['Daily_Return'].rolling(window=window).std() * np.sqrt(252)  # Annualized
    
    return df

def get_market_indices():
    """
    Get data for major Indian market indices
    
    Returns:
    dict: Dictionary with index data
    """
    indices = {
        'NIFTY 50': '^NSEI',
        'SENSEX': '^BSESN',
        'NIFTY Bank': '^NSEBANK',
        'NIFTY IT': '^CNXIT',
        'NIFTY Pharma': '^CNXPHARMA',
        'NIFTY Auto': '^CNXAUTO',
        'NIFTY FMCG': '^CNXFMCG',
        'NIFTY Metal': '^CNXMETAL',
        'NIFTY Realty': '^CNXREALTY'
    }
    
    index_data = {}
    for name, ticker in indices.items():
        data = get_stock_data(ticker, period='1y')
        if data is not None:
            index_data[name] = data
    
    return index_data

def get_real_time_quotes(tickers):
    """
    Get real-time quotes for a list of tickers
    
    Parameters:
    tickers (list): List of ticker symbols
    
    Returns:
    pd.DataFrame: DataFrame with latest quotes
    """
    try:
        if isinstance(tickers, str):
            tickers = [tickers]
            
        quotes = []
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            
            # Get the latest price info
            try:
                info = stock.info
                last_price = info.get('regularMarketPrice', None) or info.get('currentPrice', None)
                previous_close = info.get('regularMarketPreviousClose', None) or info.get('previousClose', None)
                day_high = info.get('dayHigh', None)
                day_low = info.get('dayLow', None)
                volume = info.get('volume', None)
                
                if last_price and previous_close:
                    change = last_price - previous_close
                    change_percent = (change / previous_close) * 100
                else:
                    change = None
                    change_percent = None
                
                quotes.append({
                    'Ticker': ticker,
                    'Last Price': last_price,
                    'Change': change,
                    'Change %': change_percent,
                    'Day High': day_high,
                    'Day Low': day_low,
                    'Volume': volume,
                    'Time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                print(f"Error getting quote for {ticker}: {e}")
                continue
        
        if not quotes:
            return None
            
        return pd.DataFrame(quotes)
    except Exception as e:
        print(f"Error getting real-time quotes: {e}")
        return None

def get_futures_options_data(ticker, selected_expiration=None):
    """
    Get futures and options data for a given ticker
    
    Parameters:
    ticker (str): Stock ticker symbol
    selected_expiration (str, optional): Specific expiration date to use
    
    Returns:
    dict: Dictionary with futures and options data
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get options expiration dates
        expirations = stock.options
        
        if not expirations:
            return None
        
        # Use the specified expiration or the nearest one
        target_expiration = selected_expiration if selected_expiration in expirations else expirations[0]
        calls = stock.option_chain(target_expiration).calls
        puts = stock.option_chain(target_expiration).puts
        
        # Get current stock price for context
        current_price = stock.info.get('regularMarketPrice', None) or stock.info.get('currentPrice', None)
        
        # Calculate Greeks and key metrics for options (simplified approximation)
        # Note: For real applications, use proper options pricing models
        if not calls.empty and 'strike' in calls.columns and 'impliedVolatility' in calls.columns:
            # Add moneyness to identify ITM, ATM, OTM options
            if current_price:
                calls['moneyness'] = (current_price / calls['strike']) - 1
                puts['moneyness'] = (puts['strike'] / current_price) - 1
                
                # Classify options by moneyness
                def classify_moneyness(value):
                    if value > 0.03:
                        return "ITM"  # In The Money
                    elif value < -0.03:
                        return "OTM"  # Out of The Money
                    else:
                        return "ATM"  # At The Money
                
                calls['status'] = calls['moneyness'].apply(classify_moneyness)
                puts['status'] = puts['moneyness'].apply(classify_moneyness)
                
                # Calculate theoretical theta (time decay)
                # This is a very simplified approximation
                days_to_expiry = (pd.to_datetime(target_expiration) - pd.Timestamp.now()).days
                if days_to_expiry > 0:
                    calls['theta'] = -1 * (calls['impliedVolatility'] * calls['strike'] * 0.01) / (2 * np.sqrt(days_to_expiry))
                    puts['theta'] = -1 * (puts['impliedVolatility'] * puts['strike'] * 0.01) / (2 * np.sqrt(days_to_expiry))
        
        # Return in a structured format
        return {
            'expiration_date': target_expiration,
            'calls': calls,
            'puts': puts,
            'current_price': current_price,
            'all_expirations': expirations
        }
    except Exception as e:
        print(f"Error fetching options data for {ticker}: {e}")
        return None

def forecast_futures_indices(ticker, days_forward=5):
    """
    Simple forecast for futures indices based on historical volatility and trend
    
    Parameters:
    ticker (str): Ticker symbol for the index
    days_forward (int): Number of days to forecast
    
    Returns:
    dict: Forecast data with predictions and confidence intervals
    """
    try:
        # Get historical data
        data = get_stock_data(ticker, period='60d')
        
        if data is None or len(data) < 30:
            return None
            
        # Calculate log returns and volatility
        data['log_returns'] = np.log(data['Close'] / data['Close'].shift(1))
        
        # Remove NaN values
        data = data.dropna()
        
        # Calculate statistics
        mean_return = data['log_returns'].mean()
        std_return = data['log_returns'].std()
        
        # Last closing price
        last_price = data['Close'].iloc[-1]
        
        # Generate forecasts and confidence intervals
        forecast = []
        price_pred = last_price
        
        # Current date
        start_date = pd.Timestamp.now().date()
        
        for i in range(1, days_forward + 1):
            # Add days, but skip weekends
            current_date = start_date + pd.Timedelta(days=i)
            if current_date.weekday() >= 5:  # Skip Saturday (5) and Sunday (6)
                continue
                
            # Calculate forecast values
            price_pred = price_pred * np.exp(mean_return)
            lower_bound = price_pred * np.exp(-1.96 * std_return * np.sqrt(i))
            upper_bound = price_pred * np.exp(1.96 * std_return * np.sqrt(i))
            
            forecast.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'prediction': price_pred,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            })
        
        return {
            'ticker': ticker,
            'forecast': forecast,
            'last_price': last_price,
            'mean_daily_return': mean_return,
            'daily_volatility': std_return
        }
    except Exception as e:
        print(f"Error forecasting futures indices for {ticker}: {e}")
        return None
