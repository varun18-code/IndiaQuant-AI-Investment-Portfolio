import pandas as pd
import numpy as np
from datetime import datetime
from utils.stock_data import get_stock_data, calculate_stock_returns

class Portfolio:
    def __init__(self):
        """Initialize empty portfolio"""
        self.holdings = {}  # Stock holdings
        self.mutual_funds = {}  # Mutual fund holdings
        self.transactions = []
    
    def add_position(self, ticker, shares, purchase_price, purchase_date, asset_type='stock'):
        """
        Add a position to the portfolio
        
        Parameters:
        ticker (str): Stock ticker symbol or mutual fund code
        shares (float): Number of shares or units
        purchase_price (float): Price per share or NAV per unit
        purchase_date (str): Date of purchase in 'YYYY-MM-DD' format
        asset_type (str): Type of asset - 'stock' or 'mutual_fund'
        """
        # Choose the appropriate dictionary based on asset type
        holdings_dict = self.mutual_funds if asset_type == 'mutual_fund' else self.holdings
        
        if ticker in holdings_dict:
            # Update existing position
            existing_shares = holdings_dict[ticker]['shares']
            existing_cost = holdings_dict[ticker]['shares'] * holdings_dict[ticker]['avg_price']
            new_cost = shares * purchase_price
            total_shares = existing_shares + shares
            avg_price = (existing_cost + new_cost) / total_shares
            
            holdings_dict[ticker] = {
                'shares': total_shares,
                'avg_price': avg_price,
                'purchase_date': holdings_dict[ticker]['purchase_date'],  # Keep original purchase date
                'asset_type': asset_type
            }
        else:
            # Add new position
            holdings_dict[ticker] = {
                'shares': shares,
                'avg_price': purchase_price,
                'purchase_date': purchase_date,
                'asset_type': asset_type
            }
        
        # Record transaction
        self.transactions.append({
            'ticker': ticker,
            'action': 'buy',
            'shares': shares,
            'price': purchase_price,
            'date': purchase_date,
            'asset_type': asset_type
        })
    
    def remove_position(self, ticker, shares, sell_price, sell_date, asset_type='stock'):
        """
        Remove (sell) a position from the portfolio
        
        Parameters:
        ticker (str): Stock ticker symbol or mutual fund code
        shares (float): Number of shares or units to sell
        sell_price (float): Price per share or NAV per unit
        sell_date (str): Date of sale in 'YYYY-MM-DD' format
        asset_type (str): Type of asset - 'stock' or 'mutual_fund'
        
        Returns:
        bool: True if successful, False otherwise
        """
        # Choose the appropriate dictionary based on asset type
        holdings_dict = self.mutual_funds if asset_type == 'mutual_fund' else self.holdings
        
        if ticker not in holdings_dict:
            return False
        
        if shares > holdings_dict[ticker]['shares']:
            return False
        
        # Update position
        holdings_dict[ticker]['shares'] -= shares
        
        # If all shares sold, remove position
        if holdings_dict[ticker]['shares'] <= 0:
            del holdings_dict[ticker]
        
        # Record transaction
        self.transactions.append({
            'ticker': ticker,
            'action': 'sell',
            'shares': shares,
            'price': sell_price,
            'date': sell_date,
            'asset_type': asset_type
        })
        
        return True
        
    def add_mutual_fund(self, fund_code, units, nav, purchase_date, fund_name=None):
        """
        Add a mutual fund to the portfolio
        
        Parameters:
        fund_code (str): Mutual fund code
        units (float): Number of units
        nav (float): Net Asset Value per unit
        purchase_date (str): Date of purchase in 'YYYY-MM-DD' format
        fund_name (str): Optional name of the fund for better display
        """
        # Use the add_position method with asset_type='mutual_fund'
        self.add_position(fund_code, units, nav, purchase_date, asset_type='mutual_fund')
        
        # If fund name is provided, store it separately
        if fund_name:
            if 'fund_names' not in self.__dict__:
                self.fund_names = {}
            self.fund_names[fund_code] = fund_name
    
    def remove_mutual_fund(self, fund_code, units, nav, sell_date):
        """
        Remove (redeem) mutual fund units from the portfolio
        
        Parameters:
        fund_code (str): Mutual fund code
        units (float): Number of units to redeem
        nav (float): Net Asset Value per unit
        sell_date (str): Date of redemption in 'YYYY-MM-DD' format
        
        Returns:
        bool: True if successful, False otherwise
        """
        # Use the remove_position method with asset_type='mutual_fund'
        return self.remove_position(fund_code, units, nav, sell_date, asset_type='mutual_fund')
    
    def get_portfolio_value(self):
        """
        Calculate current portfolio value including stocks and mutual funds
        
        Returns:
        dict: Portfolio value information
        """
        total_value = 0
        total_cost = 0
        positions = []
        mutual_fund_positions = []
        
        # Calculate stock holdings value
        for ticker, position in self.holdings.items():
            # Get current price
            current_data = get_stock_data(ticker, period='1d')
            if current_data is not None and not current_data.empty:
                current_price = current_data['Close'].iloc[-1]
                shares = position['shares']
                avg_price = position['avg_price']
                
                cost_basis = shares * avg_price
                current_value = shares * current_price
                gain_loss = current_value - cost_basis
                gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                
                positions.append({
                    'ticker': ticker,
                    'shares': shares,
                    'avg_price': avg_price,
                    'current_price': current_price,
                    'cost_basis': cost_basis,
                    'current_value': current_value,
                    'gain_loss': gain_loss,
                    'gain_loss_pct': gain_loss_pct,
                    'asset_type': 'stock'
                })
                
                total_value += current_value
                total_cost += cost_basis
        
        # Calculate mutual fund holdings value
        for fund_code, position in self.mutual_funds.items():
            # For mutual funds, simulate getting current NAV (usually would come from an API)
            try:
                # Get the fund name if available
                fund_name = self.fund_names[fund_code] if hasattr(self, 'fund_names') and fund_code in self.fund_names else fund_code
                
                # Simulate a NAV change based on purchase date
                purchase_date = datetime.strptime(position['purchase_date'], '%Y-%m-%d')
                days_held = (datetime.now() - purchase_date).days
                
                # Simulate a reasonable growth rate (using a dampened random walk)
                import random
                random.seed(hash(fund_code))  # Use fund code as seed for consistent results
                
                # Simulate an annual return between 8-16% for equity funds, 5-8% for debt funds
                if 'EQUITY' in fund_code or 'GROWTH' in fund_code:
                    annual_return = random.uniform(0.08, 0.16)
                else:
                    annual_return = random.uniform(0.05, 0.08)
                
                daily_return = annual_return / 365
                
                # Simulate NAV growth
                current_nav = position['avg_price'] * (1 + daily_return) ** days_held
                
                units = position['shares']
                avg_nav = position['avg_price']
                
                cost_basis = units * avg_nav
                current_value = units * current_nav
                gain_loss = current_value - cost_basis
                gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                
                mutual_fund_positions.append({
                    'ticker': fund_code,
                    'fund_name': fund_name,
                    'units': units,
                    'avg_nav': avg_nav,
                    'current_nav': current_nav,
                    'cost_basis': cost_basis,
                    'current_value': current_value,
                    'gain_loss': gain_loss,
                    'gain_loss_pct': gain_loss_pct,
                    'asset_type': 'mutual_fund'
                })
                
                total_value += current_value
                total_cost += cost_basis
            except Exception as e:
                print(f"Error calculating mutual fund value for {fund_code}: {e}")
        
        # Calculate total portfolio gain/loss
        total_gain_loss = total_value - total_cost
        total_gain_loss_pct = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
        
        # Combine positions for overall portfolio view
        all_positions = positions + mutual_fund_positions
        
        return {
            'positions': positions,  # Stock positions
            'mutual_fund_positions': mutual_fund_positions,  # Mutual fund positions
            'all_positions': all_positions,  # All positions combined
            'total_value': total_value,
            'total_cost': total_cost,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_pct': total_gain_loss_pct
        }
    
    def get_portfolio_returns(self, period='1y'):
        """
        Calculate portfolio returns over time
        
        Parameters:
        period (str): Time period for returns calculation
        
        Returns:
        pd.DataFrame: DataFrame with portfolio returns over time
        """
        if not self.holdings:
            return None
        
        # Get stock data for each holding, including mutual funds
        stock_data = {}
        
        # Add stock returns
        for ticker in self.holdings:
            data = get_stock_data(ticker, period=period)
            if data is not None:
                stock_data[ticker] = calculate_stock_returns(data)
        
        # Add mutual fund returns (using simulated data)
        for fund_code in self.mutual_funds:
            # For mutual funds, we'll simulate returns data
            try:
                # Generate a series of dates (make sure they're timezone-naive)
                today = datetime.now().replace(tzinfo=None)
                if period == '1y':
                    start_date = today - pd.Timedelta(days=365)
                elif period == '6mo':
                    start_date = today - pd.Timedelta(days=180)
                elif period == '3mo':
                    start_date = today - pd.Timedelta(days=90)
                elif period == '1mo':
                    start_date = today - pd.Timedelta(days=30)
                else:
                    start_date = today - pd.Timedelta(days=365)  # Default to 1y
                
                # Create timezone-naive date range
                date_range = pd.date_range(start=start_date, end=today, freq='B').tz_localize(None)
                
                # Simulate returns based on fund type
                import random
                random.seed(hash(fund_code))  # Use fund code as seed for consistent results
                
                # Simulate returns based on fund type (equity vs debt)
                if 'EQUITY' in fund_code or 'GROWTH' in fund_code:
                    mean_return = 0.00035  # ~12% annualized
                    std_dev = 0.008  # Higher volatility for equity
                else:
                    mean_return = 0.00020  # ~7% annualized
                    std_dev = 0.003  # Lower volatility for debt
                
                # Generate random returns with appropriate mean and standard deviation
                daily_returns = np.random.normal(mean_return, std_dev, len(date_range))
                
                # Create a DataFrame with these returns
                fund_df = pd.DataFrame({
                    'Close': (1 + pd.Series(daily_returns)).cumprod() * 50,  # Start with NAV of 50
                    'Daily_Return': daily_returns
                }, index=date_range)
                
                stock_data[fund_code] = fund_df
            except Exception as e:
                print(f"Error simulating returns for mutual fund {fund_code}: {e}")
        
        if not stock_data:
            return None
        
        # Get common date range - making sure to normalize timestamps to avoid timezone issues
        start_dates = []
        end_dates = []
        for df in stock_data.values():
            # Remove timezone info if present to avoid comparison issues
            if df.index[0].tzinfo is not None:
                df.index = df.index.tz_localize(None)
            start_dates.append(df.index[0])
            end_dates.append(df.index[-1])
        
        start_date = max(start_dates)
        end_date = min(end_dates)
        
        # Prepare portfolio returns dataframe
        portfolio_df = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))
        
        # Calculate combined investment value of stocks and mutual funds
        total_investment = sum([self.holdings[ticker]['shares'] * self.holdings[ticker]['avg_price'] for ticker in self.holdings])
        total_investment += sum([self.mutual_funds[fund]['shares'] * self.mutual_funds[fund]['avg_price'] for fund in self.mutual_funds])
        
        # Add stock weighted returns
        for ticker, data in stock_data.items():
            # Determine if this is a stock or mutual fund
            if ticker in self.holdings:
                weight = (self.holdings[ticker]['shares'] * self.holdings[ticker]['avg_price']) / total_investment
            elif ticker in self.mutual_funds:
                weight = (self.mutual_funds[ticker]['shares'] * self.mutual_funds[ticker]['avg_price']) / total_investment
            else:
                weight = 0
                
            # Get returns for the common date range
            if 'Daily_Return' in data.columns and start_date in data.index and end_date in data.index:
                ticker_returns = data.loc[start_date:end_date, 'Daily_Return']
                portfolio_df[f'{ticker}_return'] = ticker_returns * weight
        
        # Calculate portfolio daily return
        portfolio_df['Portfolio_Daily_Return'] = portfolio_df.sum(axis=1)
        
        # Calculate cumulative return
        portfolio_df['Portfolio_Cumulative_Return'] = (1 + portfolio_df['Portfolio_Daily_Return']).cumprod() - 1
        
        return portfolio_df
    
    def calculate_portfolio_metrics(self, period='1y'):
        """
        Calculate portfolio performance metrics
        
        Parameters:
        period (str): Time period for metrics calculation
        
        Returns:
        dict: Dictionary with portfolio metrics
        """
        portfolio_returns = self.get_portfolio_returns(period)
        
        if portfolio_returns is None or portfolio_returns.empty:
            return {
                'annualized_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
        
        # Annualized return
        total_days = len(portfolio_returns)
        cumulative_return = portfolio_returns['Portfolio_Cumulative_Return'].iloc[-1]
        annualized_return = (1 + cumulative_return) ** (252 / total_days) - 1
        
        # Volatility
        daily_std = portfolio_returns['Portfolio_Daily_Return'].std()
        annualized_volatility = daily_std * np.sqrt(252)
        
        # Sharpe ratio (assuming risk-free rate of 0.02)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility if annualized_volatility > 0 else 0
        
        # Maximum drawdown
        cum_returns = portfolio_returns['Portfolio_Cumulative_Return']
        running_max = cum_returns.cummax()
        drawdown = (cum_returns / running_max) - 1
        max_drawdown = drawdown.min()
        
        return {
            'annualized_return': annualized_return * 100,  # Convert to percentage
            'volatility': annualized_volatility * 100,  # Convert to percentage
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100  # Convert to percentage
        }

def save_portfolio(portfolio):
    """
    Save portfolio to session state
    
    Parameters:
    portfolio (Portfolio): Portfolio object to save
    """
    import streamlit as st
    st.session_state['portfolio'] = portfolio

def load_portfolio():
    """
    Load portfolio from session state
    
    Returns:
    Portfolio: Portfolio object
    """
    import streamlit as st
    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = Portfolio()
    return st.session_state['portfolio']

def get_sample_portfolio():
    """
    Create a sample portfolio of Indian stocks and mutual funds for demonstration
    
    Returns:
    Portfolio: Sample portfolio
    """
    portfolio = Portfolio()
    
    # Add diverse sample positions for Indian stocks representing different sectors
    # Format: add_position(ticker, shares, purchase_price, purchase_date)
    # Large Cap / Blue Chip
    portfolio.add_position('RELIANCE.NS', 15, 2450.0, '2022-01-15')  # Reliance Industries (Oil & Gas, Telecom, Retail)
    portfolio.add_position('TCS.NS', 8, 3500.0, '2022-02-10')        # Tata Consultancy Services (IT)
    portfolio.add_position('INFY.NS', 20, 1800.0, '2022-03-05')      # Infosys (IT)
    portfolio.add_position('HDFCBANK.NS', 10, 1500.0, '2022-04-20')  # HDFC Bank (Banking)
    
    # Mid-Cap
    portfolio.add_position('BAJFINANCE.NS', 25, 6500.0, '2022-05-12')  # Bajaj Finance (Finance)
    portfolio.add_position('ASIANPAINT.NS', 8, 3200.0, '2022-06-05')   # Asian Paints (Consumer)
    portfolio.add_position('MARUTI.NS', 5, 8500.0, '2022-07-10')       # Maruti Suzuki (Automotive)
    
    # Sectoral Diversity
    portfolio.add_position('SUNPHARMA.NS', 15, 850.0, '2022-08-15')    # Sun Pharma (Pharmaceuticals)
    portfolio.add_position('POWERGRID.NS', 40, 210.0, '2022-09-08')    # Power Grid (Utilities)
    portfolio.add_position('ADANIPORTS.NS', 18, 780.0, '2022-10-12')   # Adani Ports (Infrastructure)
    portfolio.add_position('HCLTECH.NS', 12, 1150.0, '2022-11-08')     # HCL Technologies (IT)
    portfolio.add_position('BRITANNIA.NS', 6, 3900.0, '2022-12-15')    # Britannia Industries (FMCG)
    
    # Add sample mutual funds - using standard Indian mutual fund schemes
    # Format: add_mutual_fund(fund_code, units, nav, purchase_date, fund_name)
    
    # Equity Funds
    portfolio.add_mutual_fund(
        'INF179K01BB8', 500, 85.25, '2022-02-05', 
        'HDFC Top 100 Fund - Direct Plan - Growth Option'
    )
    portfolio.add_mutual_fund(
        'INF209K01VL4', 750, 125.50, '2022-03-15', 
        'ICICI Prudential Bluechip Fund - Direct Plan - Growth Option'
    )
    portfolio.add_mutual_fund(
        'INF846K01PE0', 1000, 45.75, '2022-04-20', 
        'Axis Long Term Equity Fund - Direct Plan - Growth Option'
    )
    
    # Debt Funds
    portfolio.add_mutual_fund(
        'INF090I01KJ8', 2000, 35.40, '2022-05-10', 
        'Aditya Birla Sun Life Corporate Bond Fund - Direct Plan - Growth Option'
    )
    
    # Hybrid Funds
    portfolio.add_mutual_fund(
        'INF109K01VK7', 1500, 42.30, '2022-07-05', 
        'SBI Equity Hybrid Fund - Direct Plan - Growth Option'
    )
    
    # Index Funds
    portfolio.add_mutual_fund(
        'INF204KB14M2', 1200, 150.25, '2022-09-15', 
        'UTI Nifty Index Fund - Direct Plan - Growth Option'
    )
    
    return portfolio
