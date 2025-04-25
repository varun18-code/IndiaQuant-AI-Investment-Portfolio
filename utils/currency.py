import pandas as pd
from datetime import datetime, timedelta

# Default USD to INR conversion rate (approximate)
DEFAULT_USD_TO_INR = 83.0

def convert_usd_to_inr(amount, rate=DEFAULT_USD_TO_INR):
    """
    Convert USD amount to INR
    
    Parameters:
    amount (float): Amount in USD
    rate (float): Conversion rate (INR per USD)
    
    Returns:
    float: Amount in INR
    """
    return amount * rate

def convert_price_data_to_inr(df, rate=DEFAULT_USD_TO_INR):
    """
    Convert all price columns in a DataFrame from USD to INR
    
    Parameters:
    df (pd.DataFrame): DataFrame with price data
    rate (float): Conversion rate (INR per USD)
    
    Returns:
    pd.DataFrame: DataFrame with prices in INR
    """
    if df is None or df.empty:
        return df
    
    # Create a copy to avoid modifying the original
    df_inr = df.copy()
    
    # Columns to convert
    price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close']
    
    # Convert price columns
    for col in price_columns:
        if col in df_inr.columns:
            df_inr[col] = df_inr[col] * rate
    
    return df_inr

def format_currency(amount, currency='₹', show_abbreviation=True):
    """
    Format a number as currency in Indian format
    
    Parameters:
    amount (float): Amount to format
    currency (str): Currency symbol
    show_abbreviation (bool): If True, show Cr/L/K abbreviations for large amounts
    
    Returns:
    str: Formatted currency string with Indian number system
    """
    if amount is None:
        return f"{currency}0.00"
    
    # Format with Indian number system (commas after 3 digits from right, then after 2 digits)
    def indian_format(n):
        # Convert to string with 2 decimal places
        s = '{:.2f}'.format(n)
        integer_part, decimal_part = s.split('.')
        
        # Format integer part with commas (Indian system)
        result = ""
        
        # Handle negative numbers
        is_negative = False
        if integer_part.startswith('-'):
            is_negative = True
            integer_part = integer_part[1:]
        
        # Apply Indian number system
        length = len(integer_part)
        if length <= 3:
            result = integer_part
        else:
            # Add commas - first after 3 from right, then every 2 digits
            result = integer_part[-3:]
            integer_part = integer_part[:-3]
            
            # Add commas after every 2 digits
            while integer_part:
                if len(integer_part) >= 2:
                    result = integer_part[-2:] + ',' + result
                    integer_part = integer_part[:-2]
                else:
                    result = integer_part + ',' + result
                    break
        
        # Add negative sign back if needed
        if is_negative:
            result = '-' + result
            
        return f"{result}.{decimal_part}"
    
    if show_abbreviation:
        if amount >= 10000000:  # Above 1 crore
            return f"{currency}{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # Above 1 lakh
            return f"{currency}{amount/100000:.2f} L"
        elif amount >= 1000:  # Above 1 thousand
            return f"{currency}{amount/1000:.2f} K"
        else:
            return f"{currency}{amount:.2f}"
    else:
        # Format with Indian number system with commas
        return f"{currency}{indian_format(amount)}"

def format_market_cap(amount, in_inr=True, show_full=False):
    """
    Format market cap in the Indian numbering system
    
    Parameters:
    amount (float): Market cap amount
    in_inr (bool): If True, amount is in INR, otherwise in USD
    show_full (bool): If True, show full amount with commas instead of abbreviations
    
    Returns:
    str: Formatted market cap string
    """
    if amount is None:
        return "N/A"
    
    # Convert to INR if needed
    if not in_inr:
        amount = convert_usd_to_inr(amount)
    
    if show_full:
        # Use the indian_format function from format_currency
        return format_currency(amount, currency="₹", show_abbreviation=False)
    else:
        if amount >= 10000000000:  # Above 1000 crore
            return f"₹{amount/10000000000:.2f} Thousand Cr"
        elif amount >= 10000000:  # Above 1 crore
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # Above 1 lakh
            return f"₹{amount/100000:.2f} L"
        else:
            return format_currency(amount, show_abbreviation=False)

def get_inr_symbol():
    """
    Get the Indian Rupee symbol
    
    Returns:
    str: Rupee symbol
    """
    return "₹"