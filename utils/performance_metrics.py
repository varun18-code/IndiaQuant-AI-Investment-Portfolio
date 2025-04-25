import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """
    Calculate Sharpe ratio for a given return series
    
    Parameters:
    returns (pd.Series): Series of returns
    risk_free_rate (float): Annual risk-free rate
    
    Returns:
    float: Sharpe ratio
    """
    if returns is None or len(returns) < 2:
        return 0
    
    # Convert annual risk-free rate to match return frequency
    # Assuming returns are daily
    rf_daily = (1 + risk_free_rate) ** (1/252) - 1
    
    excess_returns = returns - rf_daily
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252)

def calculate_sortino_ratio(returns, risk_free_rate=0.02):
    """
    Calculate Sortino ratio for a given return series
    
    Parameters:
    returns (pd.Series): Series of returns
    risk_free_rate (float): Annual risk-free rate
    
    Returns:
    float: Sortino ratio
    """
    if returns is None or len(returns) < 2:
        return 0
    
    # Convert annual risk-free rate to match return frequency
    # Assuming returns are daily
    rf_daily = (1 + risk_free_rate) ** (1/252) - 1
    
    excess_returns = returns - rf_daily
    
    # Calculate downside deviation (only negative returns)
    negative_returns = excess_returns[excess_returns < 0]
    downside_deviation = np.sqrt(np.mean(negative_returns ** 2)) if len(negative_returns) > 0 else 0.0001
    
    return excess_returns.mean() / downside_deviation * np.sqrt(252)

def calculate_max_drawdown(returns):
    """
    Calculate maximum drawdown for a given return series
    
    Parameters:
    returns (pd.Series): Series of returns
    
    Returns:
    float: Maximum drawdown
    """
    if returns is None or len(returns) < 2:
        return 0
    
    # Calculate cumulative returns
    cum_returns = (1 + returns).cumprod()
    
    # Calculate running maximum
    running_max = cum_returns.cummax()
    
    # Calculate drawdown
    drawdown = (cum_returns / running_max) - 1
    
    # Find maximum drawdown
    max_drawdown = drawdown.min()
    
    return max_drawdown

def calculate_alpha_beta(returns, benchmark_returns):
    """
    Calculate alpha and beta for a given return series against a benchmark
    
    Parameters:
    returns (pd.Series): Series of returns
    benchmark_returns (pd.Series): Series of benchmark returns
    
    Returns:
    tuple: (alpha, beta)
    """
    if returns is None or benchmark_returns is None or len(returns) < 2 or len(benchmark_returns) < 2:
        return 0, 0
    
    # Make sure the indices align
    aligned_returns = pd.DataFrame({
        'returns': returns,
        'benchmark': benchmark_returns
    }).dropna()
    
    if len(aligned_returns) < 2:
        return 0, 0
    
    # Calculate beta (covariance / variance)
    covariance = aligned_returns['returns'].cov(aligned_returns['benchmark'])
    variance = aligned_returns['benchmark'].var()
    beta = covariance / variance if variance > 0 else 0
    
    # Calculate alpha
    alpha = aligned_returns['returns'].mean() - beta * aligned_returns['benchmark'].mean()
    
    # Annualize alpha (assuming daily returns)
    alpha = alpha * 252
    
    return alpha, beta

def calculate_information_ratio(returns, benchmark_returns):
    """
    Calculate information ratio for a given return series against a benchmark
    
    Parameters:
    returns (pd.Series): Series of returns
    benchmark_returns (pd.Series): Series of benchmark returns
    
    Returns:
    float: Information ratio
    """
    if returns is None or benchmark_returns is None or len(returns) < 2 or len(benchmark_returns) < 2:
        return 0
    
    # Make sure the indices align
    aligned_returns = pd.DataFrame({
        'returns': returns,
        'benchmark': benchmark_returns
    }).dropna()
    
    if len(aligned_returns) < 2:
        return 0
    
    # Calculate active returns
    active_returns = aligned_returns['returns'] - aligned_returns['benchmark']
    
    # Calculate tracking error
    tracking_error = active_returns.std()
    
    # Calculate information ratio
    information_ratio = active_returns.mean() / tracking_error if tracking_error > 0 else 0
    
    # Annualize information ratio (assuming daily returns)
    information_ratio = information_ratio * np.sqrt(252)
    
    return information_ratio

def calculate_performance_metrics(returns, benchmark_returns=None, risk_free_rate=0.02):
    """
    Calculate comprehensive performance metrics for a given return series
    
    Parameters:
    returns (pd.Series): Series of returns
    benchmark_returns (pd.Series): Series of benchmark returns
    risk_free_rate (float): Annual risk-free rate
    
    Returns:
    dict: Dictionary with performance metrics
    """
    if returns is None or len(returns) < 2:
        return {
            'total_return': 0,
            'annualized_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'max_drawdown': 0,
            'alpha': 0,
            'beta': 0,
            'information_ratio': 0
        }
    
    # Calculate total return
    total_return = (1 + returns).prod() - 1
    
    # Calculate annualized return
    num_years = len(returns) / 252  # Assuming daily returns
    annualized_return = (1 + total_return) ** (1 / num_years) - 1 if num_years > 0 else 0
    
    # Calculate volatility
    volatility = returns.std() * np.sqrt(252)  # Annualized
    
    # Calculate other metrics
    sharpe_ratio = calculate_sharpe_ratio(returns, risk_free_rate)
    sortino_ratio = calculate_sortino_ratio(returns, risk_free_rate)
    max_drawdown = calculate_max_drawdown(returns)
    
    # Calculate alpha and beta if benchmark is provided
    alpha, beta = 0, 0
    information_ratio = 0
    if benchmark_returns is not None:
        alpha, beta = calculate_alpha_beta(returns, benchmark_returns)
        information_ratio = calculate_information_ratio(returns, benchmark_returns)
    
    return {
        'total_return': total_return * 100,  # Convert to percentage
        'annualized_return': annualized_return * 100,  # Convert to percentage
        'volatility': volatility * 100,  # Convert to percentage
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown * 100,  # Convert to percentage
        'alpha': alpha * 100,  # Convert to percentage
        'beta': beta,
        'information_ratio': information_ratio
    }

def calculate_risk_metrics(portfolio_returns, benchmark_returns=None):
    """
    Calculate risk metrics and value at risk for a portfolio
    
    Parameters:
    portfolio_returns (pd.Series): Series of portfolio returns
    benchmark_returns (pd.Series): Series of benchmark returns
    
    Returns:
    dict: Dictionary with risk metrics
    """
    if portfolio_returns is None or len(portfolio_returns) < 30:  # Need sufficient data for meaningful VaR
        return {
            'daily_var_95': 0,
            'daily_var_99': 0,
            'monthly_var_95': 0,
            'monthly_var_99': 0,
            'downside_deviation': 0,
            'monthly_volatility': 0,
            'correlation_to_market': 0
        }
    
    # Calculate daily Value at Risk
    daily_var_95 = np.percentile(portfolio_returns, 5)  # 95% VaR
    daily_var_99 = np.percentile(portfolio_returns, 1)  # 99% VaR
    
    # Calculate monthly returns (approximation)
    monthly_returns = [(1 + portfolio_returns.iloc[i:i+21]).prod() - 1 
                       for i in range(0, len(portfolio_returns), 21) if i+21 <= len(portfolio_returns)]
    
    # Calculate monthly Value at Risk if we have enough data
    monthly_var_95 = np.percentile(monthly_returns, 5) if len(monthly_returns) >= 10 else daily_var_95 * np.sqrt(21)
    monthly_var_99 = np.percentile(monthly_returns, 1) if len(monthly_returns) >= 10 else daily_var_99 * np.sqrt(21)
    
    # Calculate downside deviation
    negative_returns = portfolio_returns[portfolio_returns < 0]
    downside_deviation = np.sqrt(np.mean(negative_returns ** 2)) * np.sqrt(252) if len(negative_returns) > 0 else 0
    
    # Calculate monthly volatility
    monthly_volatility = np.std(monthly_returns) * np.sqrt(12) if len(monthly_returns) >= 10 else 0
    
    # Calculate correlation to market
    correlation_to_market = 0
    if benchmark_returns is not None and len(benchmark_returns) >= 30:
        # Make sure the indices align
        aligned_returns = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned_returns) >= 30:
            correlation_to_market = aligned_returns['portfolio'].corr(aligned_returns['benchmark'])
    
    return {
        'daily_var_95': abs(daily_var_95) * 100,  # Convert to positive percentage
        'daily_var_99': abs(daily_var_99) * 100,  # Convert to positive percentage
        'monthly_var_95': abs(monthly_var_95) * 100,  # Convert to positive percentage
        'monthly_var_99': abs(monthly_var_99) * 100,  # Convert to positive percentage
        'downside_deviation': downside_deviation * 100,  # Convert to percentage
        'monthly_volatility': monthly_volatility * 100 if monthly_volatility else 0,  # Convert to percentage
        'correlation_to_market': correlation_to_market
    }

def calculate_sector_allocation(portfolio):
    """
    Calculate sector allocation for a portfolio
    
    Parameters:
    portfolio (dict): Portfolio data
    
    Returns:
    dict: Sector allocation data
    """
    from utils.stock_data import get_stock_info
    
    positions = portfolio.get('positions', [])
    
    if not positions:
        return {
            'sectors': [],
            'weights': []
        }
    
    # Get sector information for each position
    sector_data = {}
    total_value = sum(pos['current_value'] for pos in positions)
    
    for pos in positions:
        ticker = pos['ticker']
        stock_info = get_stock_info(ticker)
        sector = stock_info.get('sector', 'Unknown')
        
        weight = pos['current_value'] / total_value
        
        if sector in sector_data:
            sector_data[sector] += weight
        else:
            sector_data[sector] = weight
    
    # Convert to lists for charts
    sectors = list(sector_data.keys())
    weights = [sector_data[sector] * 100 for sector in sectors]  # Convert to percentage
    
    return {
        'sectors': sectors,
        'weights': weights
    }

def calculate_asset_correlation_matrix(returns_dict):
    """
    Calculate correlation matrix for a dictionary of asset returns
    
    Parameters:
    returns_dict (dict): Dictionary with asset returns
    
    Returns:
    pd.DataFrame: Correlation matrix
    """
    if not returns_dict or len(returns_dict) < 2:
        return pd.DataFrame()
    
    # Create a dataframe with all returns
    returns_df = pd.DataFrame(returns_dict)
    
    # Calculate correlation matrix
    correlation_matrix = returns_df.corr()
    
    return correlation_matrix
