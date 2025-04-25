import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier

# Handle talib import - create a mock implementation since it's not available
class TALib:
    """Mock implementation of TA-Lib functions"""
    
    @staticmethod
    def RSI(values, timeperiod=14):
        # Manual RSI calculation
        delta = pd.Series(values).diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=timeperiod).mean()
        avg_loss = loss.rolling(window=timeperiod).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def MACD(values, fastperiod=12, slowperiod=26, signalperiod=9):
        values_series = pd.Series(values)
        exp1 = values_series.ewm(span=fastperiod, adjust=False).mean()
        exp2 = values_series.ewm(span=slowperiod, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signalperiod, adjust=False).mean()
        hist = macd - signal
        return macd.values, signal.values, hist.values
    
    @staticmethod
    def BBANDS(values, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
        values_series = pd.Series(values)
        middle = values_series.rolling(window=timeperiod).mean()
        stddev = values_series.rolling(window=timeperiod).std()
        upper = middle + (stddev * nbdevup)
        lower = middle - (stddev * nbdevdn)
        return upper.values, middle.values, lower.values
    
    @staticmethod
    def STOCH(high, low, close, fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        close_series = pd.Series(close)
        
        high_roll = high_series.rolling(window=fastk_period).max()
        low_roll = low_series.rolling(window=fastk_period).min()
        
        fastk = 100 * ((close_series - low_roll) / (high_roll - low_roll))
        slowk = fastk.rolling(window=slowk_period).mean()
        slowd = slowk.rolling(window=slowd_period).mean()
        
        return slowk.values, slowd.values
    
    @staticmethod
    def WILLR(high, low, close, timeperiod=14):
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        close_series = pd.Series(close)
        
        high_roll = high_series.rolling(window=timeperiod).max()
        low_roll = low_series.rolling(window=timeperiod).min()
        
        return -100 * ((high_roll - close_series) / (high_roll - low_roll)).values

# Use our implementation
ta = TALib()

def calculate_technical_indicators(df):
    """
    Calculate technical indicators for pattern recognition
    
    Parameters:
    df (pd.DataFrame): DataFrame with OHLC price data
    
    Returns:
    pd.DataFrame: DataFrame with technical indicators
    """
    if df is None or df.empty:
        return None
    
    # Create a copy of the dataframe
    data = df.copy()
    
    # Calculate basic technical indicators
    # Moving Averages
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA10'] = data['Close'].rolling(window=10).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()
    
    # Relative Strength Index
    try:
        # Try to use talib
        data['RSI'] = ta.RSI(data['Close'].values, timeperiod=14)
    except:
        # Manual RSI calculation if talib is not available
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD (Moving Average Convergence Divergence)
    try:
        # Try to use talib
        macd, macd_signal, macd_hist = ta.MACD(data['Close'].values, 
                                               fastperiod=12, slowperiod=26, signalperiod=9)
        data['MACD'] = macd
        data['MACD_Signal'] = macd_signal
        data['MACD_Hist'] = macd_hist
    except:
        # Manual MACD calculation if talib is not available
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
    
    # Bollinger Bands
    try:
        # Try to use talib
        upper, middle, lower = ta.BBANDS(data['Close'].values, timeperiod=20, 
                                         nbdevup=2, nbdevdn=2, matype=0)
        data['BB_Upper'] = upper
        data['BB_Middle'] = middle
        data['BB_Lower'] = lower
    except:
        # Manual Bollinger Bands calculation if talib is not available
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        data['BB_Std'] = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (data['BB_Std'] * 2)
        data['BB_Lower'] = data['BB_Middle'] - (data['BB_Std'] * 2)
    
    # Stochastic Oscillator
    try:
        # Try to use talib
        slowk, slowd = ta.STOCH(data['High'].values, data['Low'].values, data['Close'].values, 
                                fastk_period=14, slowk_period=3, slowk_matype=0, 
                                slowd_period=3, slowd_matype=0)
        data['SlowK'] = slowk
        data['SlowD'] = slowd
    except:
        # Manual Stochastic Oscillator calculation if talib is not available
        high_14 = data['High'].rolling(window=14).max()
        low_14 = data['Low'].rolling(window=14).min()
        data['%K'] = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
        data['%D'] = data['%K'].rolling(window=3).mean()
        
    # Calculate volume indicators
    # On-Balance Volume (OBV)
    data['OBV'] = (np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum()
    
    # Volume Rate of Change
    data['Volume_ROC'] = data['Volume'].pct_change(periods=1) * 100
    
    # Add price momentum indicators
    # Rate of Change
    data['ROC'] = data['Close'].pct_change(periods=10) * 100
    
    # Williams %R
    try:
        # Try to use talib
        data['Williams_%R'] = ta.WILLR(data['High'].values, data['Low'].values, 
                                      data['Close'].values, timeperiod=14)
    except:
        # Manual Williams %R calculation if talib is not available
        high_14 = data['High'].rolling(window=14).max()
        low_14 = data['Low'].rolling(window=14).min()
        data['Williams_%R'] = -100 * ((high_14 - data['Close']) / (high_14 - low_14))
    
    # Fill NaN values
    data = data.fillna(method='bfill')
    
    return data

def identify_candlestick_patterns(df):
    """
    Identify common candlestick patterns in price data
    
    Parameters:
    df (pd.DataFrame): DataFrame with OHLC price data
    
    Returns:
    pd.DataFrame: DataFrame with candlestick pattern flags
    """
    if df is None or df.empty:
        return None
    
    # Create a copy of the dataframe
    data = df.copy()
    
    # Calculate candlestick components
    data['Body'] = abs(data['Open'] - data['Close'])
    data['UpperShadow'] = data.apply(
        lambda x: x['High'] - x['Close'] if x['Close'] > x['Open'] else x['High'] - x['Open'], 
        axis=1
    )
    data['LowerShadow'] = data.apply(
        lambda x: x['Close'] - x['Low'] if x['Close'] < x['Open'] else x['Open'] - x['Low'], 
        axis=1
    )
    
    # Simple pattern detection (manual implementation)
    # Doji
    data['Doji'] = (data['Body'] <= 0.1 * (data['High'] - data['Low']))
    
    # Hammer and Hanging Man
    data['Hammer'] = ((data['LowerShadow'] >= 2 * data['Body']) & 
                      (data['UpperShadow'] <= 0.1 * data['Body']) &
                      (data['Body'] > 0))
    
    # Shooting Star and Inverted Hammer
    data['ShootingStar'] = ((data['UpperShadow'] >= 2 * data['Body']) & 
                            (data['LowerShadow'] <= 0.1 * data['Body']) &
                            (data['Body'] > 0))
    
    # Engulfing patterns
    data['BullishEngulfing'] = False
    data['BearishEngulfing'] = False
    
    for i in range(1, len(data)):
        if (data['Close'].iloc[i] > data['Open'].iloc[i] and  # Current candle is bullish
            data['Close'].iloc[i-1] < data['Open'].iloc[i-1] and  # Previous candle is bearish
            data['Close'].iloc[i] > data['Open'].iloc[i-1] and  # Current close > previous open
            data['Open'].iloc[i] < data['Close'].iloc[i-1]):  # Current open < previous close
            data.loc[data.index[i], 'BullishEngulfing'] = True
            
        elif (data['Close'].iloc[i] < data['Open'].iloc[i] and  # Current candle is bearish
              data['Close'].iloc[i-1] > data['Open'].iloc[i-1] and  # Previous candle is bullish
              data['Close'].iloc[i] < data['Open'].iloc[i-1] and  # Current close < previous open
              data['Open'].iloc[i] > data['Close'].iloc[i-1]):  # Current open > previous close
            data.loc[data.index[i], 'BearishEngulfing'] = True
    
    return data

def detect_chart_patterns(df, window_size=20):
    """
    Detect common chart patterns like support/resistance, trends
    
    Parameters:
    df (pd.DataFrame): DataFrame with price data
    window_size (int): Window size for pattern detection
    
    Returns:
    dict: Dictionary with detected patterns
    """
    if df is None or df.empty or len(df) < window_size:
        return {"error": "Not enough data for pattern detection"}
    
    # Create a copy of the dataframe
    data = df.copy()
    
    # Calculate highs and lows for pattern detection
    rolling_high = data['High'].rolling(window=window_size, center=True).max()
    rolling_low = data['Low'].rolling(window=window_size, center=True).min()
    
    # Detect support levels (areas where price bounced off lows multiple times)
    support_levels = []
    for i in range(window_size, len(data) - window_size):
        if (data['Low'].iloc[i] <= data['Low'].iloc[i-1:i+window_size].min() * 1.01 and
            data['Low'].iloc[i] >= data['Low'].iloc[i-1:i+window_size].min() * 0.99):
            # Check if this level is close to an existing support level
            new_level = data['Low'].iloc[i]
            if not any(abs(level - new_level) / level < 0.02 for level in support_levels):
                support_levels.append(new_level)
    
    # Detect resistance levels (areas where price bounced off highs multiple times)
    resistance_levels = []
    for i in range(window_size, len(data) - window_size):
        if (data['High'].iloc[i] >= data['High'].iloc[i-1:i+window_size].max() * 0.99 and
            data['High'].iloc[i] <= data['High'].iloc[i-1:i+window_size].max() * 1.01):
            # Check if this level is close to an existing resistance level
            new_level = data['High'].iloc[i]
            if not any(abs(level - new_level) / level < 0.02 for level in resistance_levels):
                resistance_levels.append(new_level)
    
    # Detect trend
    current_close = data['Close'].iloc[-1]
    ma50_last = data['Close'].rolling(window=50).mean().iloc[-1]
    ma200_last = data['Close'].rolling(window=200).mean().iloc[-1]
    
    if current_close > ma50_last and ma50_last > ma200_last:
        trend = "Bullish"
    elif current_close < ma50_last and ma50_last < ma200_last:
        trend = "Bearish"
    else:
        trend = "Sideways"
    
    # Check for golden cross (50-day MA crosses above 200-day MA)
    golden_cross = False
    for i in range(1, min(10, len(data))):
        ma50_prev = data['Close'].rolling(window=50).mean().iloc[-i-1]
        ma200_prev = data['Close'].rolling(window=200).mean().iloc[-i-1]
        ma50_curr = data['Close'].rolling(window=50).mean().iloc[-i]
        ma200_curr = data['Close'].rolling(window=200).mean().iloc[-i]
        
        if ma50_prev < ma200_prev and ma50_curr > ma200_curr:
            golden_cross = True
            break
    
    # Check for death cross (50-day MA crosses below 200-day MA)
    death_cross = False
    for i in range(1, min(10, len(data))):
        ma50_prev = data['Close'].rolling(window=50).mean().iloc[-i-1]
        ma200_prev = data['Close'].rolling(window=200).mean().iloc[-i-1]
        ma50_curr = data['Close'].rolling(window=50).mean().iloc[-i]
        ma200_curr = data['Close'].rolling(window=200).mean().iloc[-i]
        
        if ma50_prev > ma200_prev and ma50_curr < ma200_curr:
            death_cross = True
            break
    
    # Return detected patterns
    return {
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "trend": trend,
        "golden_cross": golden_cross,
        "death_cross": death_cross
    }

def train_pattern_recognition_model(historical_data, prediction_window=5):
    """
    Train a simple model to recognize patterns and predict price movements
    
    Parameters:
    historical_data (pd.DataFrame): DataFrame with historical price data and indicators
    prediction_window (int): Number of days to predict ahead
    
    Returns:
    tuple: (trained model, scaler)
    """
    if historical_data is None or historical_data.empty:
        return None, None
    
    data = historical_data.copy()
    
    # Feature columns (technical indicators)
    feature_cols = [
        'MA5', 'MA10', 'MA20', 'MA50', 'RSI', 'MACD', 'MACD_Signal', 
        'MACD_Hist', 'BB_Upper', 'BB_Middle', 'BB_Lower', 'SlowK', 'SlowD',
        'OBV', 'Volume_ROC', 'ROC', 'Williams_%R'
    ]
    
    # Create the target variable (1 if price went up after prediction_window days, 0 otherwise)
    data['Target'] = (data['Close'].shift(-prediction_window) > data['Close']).astype(int)
    
    # Drop rows with NaN values
    data = data.dropna()
    
    if len(data) < prediction_window * 2:
        return None, None
    
    # Split the data, keeping the most recent data for validation
    train_size = int(len(data) * 0.8)
    X_train = data[feature_cols][:train_size]
    y_train = data['Target'][:train_size]
    
    # Scale the features
    scaler = MinMaxScaler(feature_range=(0, 1))
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train a random forest classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    return model, scaler

def predict_future_movement(model, scaler, current_data, feature_cols):
    """
    Predict future price movement using the trained model
    
    Parameters:
    model: Trained ML model
    scaler: Feature scaler
    current_data (pd.DataFrame): DataFrame with current price data and indicators
    feature_cols (list): List of feature column names
    
    Returns:
    float: Probability of upward movement
    """
    if model is None or scaler is None or current_data is None or current_data.empty:
        return 0.5  # Default to 50% probability if we can't make a prediction
    
    # Prepare the features
    X = current_data[feature_cols].iloc[-1:].values
    
    # Scale the features
    X_scaled = scaler.transform(X)
    
    # Make prediction
    prediction_prob = model.predict_proba(X_scaled)[0][1]
    
    return prediction_prob
