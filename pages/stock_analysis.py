import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from utils.stock_data import get_stock_data, get_stock_info, calculate_stock_returns, calculate_volatility
from utils.pattern_recognition import calculate_technical_indicators, identify_candlestick_patterns
from utils.sentiment_analysis import fetch_financial_news, analyze_news_sentiment
from utils.currency import convert_usd_to_inr, format_currency, format_market_cap

# Custom CSS for enhanced visuals
def local_css():
    st.markdown("""
    <style>
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #e9ecef;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .metric-card .label {
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 5px;
        }
        
        .metric-card .value {
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-card .change {
            font-size: 0.9rem;
        }
        
        .positive-change {
            color: #28a745;
        }
        
        .negative-change {
            color: #dc3545;
        }
        
        .neutral-change {
            color: #6c757d;
        }
        
        .tooltip {
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted #4472CA;
            cursor: help;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 250px;
            background-color: #f8f9fa;
            color: #333;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            border: 1px solid #ddd;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -125px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.85rem;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        .section-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .infobox {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 4px;
        }
        
        .chart-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        
        .indicator-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
            margin: 2px;
        }
        
        .bullish {
            background-color: rgba(40, 167, 69, 0.2);
            color: #28a745;
            border: 1px solid rgba(40, 167, 69, 0.4);
        }
        
        .bearish {
            background-color: rgba(220, 53, 69, 0.2);
            color: #dc3545;
            border: 1px solid rgba(220, 53, 69, 0.4);
        }
        
        .neutral {
            background-color: rgba(108, 117, 125, 0.2);
            color: #6c757d;
            border: 1px solid rgba(108, 117, 125, 0.4);
        }
        
        .company-info {
            border-left: 4px solid #6c757d;
            padding-left: 15px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)

# Helper functions for explanations of financial metrics
def get_metric_explanation(metric_name):
    explanations = {
        "Price/Earnings Ratio": "The P/E ratio shows how much investors are willing to pay for each rupee of earnings. A higher P/E suggests investors expect higher growth in the future.",
        "Market Cap": "Total market value of all shares outstanding. Large-cap (>₹20,000 Cr), Mid-cap (₹5,000-20,000 Cr), Small-cap (<₹5,000 Cr).",
        "52-Week Range": "The highest and lowest prices at which a stock has traded in the last 52 weeks, indicating price volatility.",
        "Dividend Yield": "Annual dividend payments relative to share price, expressed as a percentage.",
        "Volume": "Number of shares traded in a specific period, indicating market activity and liquidity.",
        "Beta": "Measure of stock's volatility compared to the overall market. Beta>1 indicates higher volatility than the market.",
        "RSI": "Relative Strength Index measures momentum on a scale of 0-100. Values above 70 suggest overbought conditions; below 30 suggest oversold.",
        "MACD": "Moving Average Convergence Divergence identifies trend direction and momentum changes.",
        "Bollinger Bands": "Volatility bands set above and below a moving average, helping identify overbought or oversold conditions.",
        "Support Level": "Price level where a downtrend can be expected to pause due to buying interest.",
        "Resistance Level": "Price level where an uptrend can be expected to pause due to selling interest.",
        "Volatility": "Statistical measure of price fluctuation. Higher volatility indicates greater price swings and potentially higher risk."
    }
    return explanations.get(metric_name, "No explanation available")

# Function to create a metric card with explanation tooltip
def create_metric_card(label, value, change=None, change_prefix="", tooltip_text=None):
    # Determine change class based on value
    if change is None:
        change_class = "neutral-change"
        change_text = ""
    else:
        change_class = "positive-change" if change >= 0 else "negative-change"
        change_sign = "+" if change > 0 else ""
        change_text = f"{change_sign}{change_prefix}{change:.2f}%" if isinstance(change, (int, float)) else change

    # Create tooltip if explanation exists
    tooltip_html = ""
    if tooltip_text:
        tooltip_html = f"""
        <div class="tooltip">ℹ️
            <span class="tooltiptext">{tooltip_text}</span>
        </div>
        """

    # Generate complete metric card HTML
    metric_html = f"""
    <div class="metric-card">
        <div class="label">{label} {tooltip_html}</div>
        <div class="value">{value}</div>
        <div class="change {change_class}">{change_text}</div>
    </div>
    """
    return metric_html

# Function to create Indian stock recommendations
def get_stock_recommendations(sector):
    # Map sectors to common Indian stocks in that sector
    sector_stocks = {
        "Financial Services": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BAJFINANCE.NS", "AXISBANK.NS"],
        "Information Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
        "Oil & Gas": ["RELIANCE.NS", "ONGC.NS", "IOC.NS", "GAIL.NS", "BPCL.NS"],
        "Automobile": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS"],
        "Consumer Goods": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "MARICO.NS"],
        "Pharmaceuticals": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "BIOCON.NS"],
        "Metals": ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "VEDL.NS", "COAL.NS"],
        "N/A": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS"]  # Default recommendations
    }
    
    # Get stocks for the sector or default if not found
    similar_stocks = sector_stocks.get(sector, sector_stocks["N/A"])
    # Shuffle to get different recommendations each time
    random.shuffle(similar_stocks)
    # Return first 3 stocks
    return similar_stocks[:3]

def show():
    """Display the stock analysis page"""
    # Apply custom CSS
    local_css()
    
    st.markdown('<h1 style="font-size: 2rem;">In-Depth Stock Analysis</h1>', unsafe_allow_html=True)
    
    # Information box about what this page offers
    st.markdown("""
    <div class="infobox">
        <strong>What you can do here:</strong> Research stocks from NSE and BSE with comprehensive technical and fundamental analysis. 
        Compare performance, view key metrics, and get insights to make informed investment decisions.
    </div>
    """, unsafe_allow_html=True)
    
    # Default ticker and time period (India-focused)
    default_ticker = "RELIANCE.NS"
    
    # Popular Indian stocks for quick selection
    popular_indian_stocks = {
        "Reliance Industries": "RELIANCE.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "HUL": "HINDUNILVR.NS",
        "SBI": "SBIN.NS",
        "Bajaj Finance": "BAJFINANCE.NS",
        "ITC": "ITC.NS",
        "L&T": "LT.NS"
    }
    
    # Select stock section with better UI
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        # Option to pick from popular stocks or enter custom
        stock_selection = st.radio(
            "Select stock by:",
            ["Popular Indian Stocks", "Custom Ticker"],
            horizontal=True
        )
        
        if stock_selection == "Popular Indian Stocks":
            selected_stock = st.selectbox(
                "Choose a stock:",
                list(popular_indian_stocks.keys())
            )
            ticker = popular_indian_stocks[selected_stock]
        else:
            ticker = st.text_input(
                "Enter Ticker Symbol (add .NS for NSE, .BO for BSE)", 
                value=default_ticker,
                help="Examples: RELIANCE.NS, TATAMOTORS.BO, INFY.NS"
            ).upper()
    
    with col2:
        # Time period selection with helpful tooltips
        time_period = st.selectbox(
            "Select Time Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=3,  # Default to 1y
            help="Choose the historical data timeframe for analysis"
        )
        
        # Add interval selection for more detailed analysis
        interval = st.selectbox(
            "Select Data Interval",
            ["1d", "1wk", "1mo"],
            index=0,  # Default to daily
            help="Choose the granularity of data points"
        )
    
    with col3:
        # Analysis type
        analysis_type = st.radio(
            "Analysis Focus:",
            ["Technical", "Fundamental", "Both"],
            index=2,  # Default to both
            help="Technical: chart patterns, indicators. Fundamental: company financials, ratios."
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add a loading indicator while fetching data
    with st.spinner(f"Fetching data for {ticker}..."):
        # Fetch stock data and info
        stock_data = get_stock_data(ticker, period=time_period, interval=interval)
        stock_info = get_stock_info(ticker)
    
    if stock_data is not None and not stock_data.empty:
        # Calculate additional metrics
        stock_data = calculate_stock_returns(stock_data)
        stock_data = calculate_volatility(stock_data)
        
        # Stock overview section
        company_name = stock_info.get('shortName', ticker)
        st.markdown(f'<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<h2 style="font-size: 1.5rem; margin-bottom: 15px;">{company_name} ({ticker}) Overview</h2>', unsafe_allow_html=True)
        
        # Company information
        st.markdown(f"""
        <div class="company-info">
            <p><strong>Sector:</strong> {stock_info.get('sector', 'N/A')}</p>
            <p><strong>Industry:</strong> {stock_info.get('industry', 'N/A')}</p>
            <p style="font-size: 0.9rem;">{stock_info.get('longBusinessSummary', '')[:300]}{'...' if len(stock_info.get('longBusinessSummary', '')) > 300 else ''}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Current price and metrics
        if stock_data is not None and not stock_data.empty:
            current_price = stock_data['Close'].iloc[-1]
            prev_close = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
            price_change = current_price - prev_close
            price_change_pct = (price_change / prev_close) * 100 if prev_close != 0 else 0
        else:
            # Handle case when stock data is None or empty
            current_price = 0
            price_change = 0
            price_change_pct = 0
            st.error("Could not retrieve stock data. Please try another ticker.")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Current Price",
                value=f"₹{current_price:.2f}",
                delta=f"{price_change_pct:.2f}%"
            )
        
        with col2:
            # 52-week high/low
            st.metric(
                label="52-Week High",
                value=f"₹{stock_info['fiftyTwoWeekHigh']:.2f}"
            )
        
        with col3:
            st.metric(
                label="52-Week Low",
                value=f"₹{stock_info['fiftyTwoWeekLow']:.2f}"
            )
        
        with col4:
            # Market cap in billions
            market_cap_b = stock_info['marketCap'] / 1_000_000_000
            st.metric(
                label="Market Cap",
                value=f"₹{market_cap_b:.2f}B"
            )
        
        # Stock price chart
        st.subheader("Price Chart")
        
        # Create tabs for different chart types
        price_tab, candlestick_tab, returns_tab = st.tabs(["Line", "Candlestick", "Returns"])
        
        with price_tab:
            # Line chart
            fig = go.Figure()
            
            if stock_data is not None and not stock_data.empty:
                fig.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#1E88E5', width=2)
                ))
            else:
                # Add empty trace with a message
                fig.add_annotation(
                    x=0.5, y=0.5,
                    text="No data available",
                    showarrow=False,
                    font=dict(size=20)
                )
            
            # Add volume as a subplot
            fig.add_trace(go.Bar(
                x=stock_data.index,
                y=stock_data['Volume'],
                name='Volume',
                marker=dict(color='rgba(0, 0, 0, 0.2)'),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title=f"{ticker} Price History",
                xaxis_title='Date',
                yaxis_title='Price (₹)',
                yaxis2=dict(
                    title='Volume',
                    titlefont=dict(color='rgba(0, 0, 0, 0.5)'),
                    tickfont=dict(color='rgba(0, 0, 0, 0.5)'),
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=500,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with candlestick_tab:
            # Candlestick chart
            fig = go.Figure()
            
            if stock_data is not None and not stock_data.empty:
                fig.add_trace(go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close'],
                    name='Price'
                ))
                
                # Add volume as a subplot
                fig.add_trace(go.Bar(
                    x=stock_data.index,
                    y=stock_data['Volume'],
                    name='Volume',
                    marker=dict(color='rgba(0, 0, 0, 0.2)'),
                    yaxis='y2'
                ))
            else:
                # Add empty trace with a message
                fig.add_annotation(
                    x=0.5, y=0.5,
                    text="No data available",
                    showarrow=False,
                    font=dict(size=20)
                )
            
            fig.update_layout(
                title=f"{ticker} Candlestick Chart",
                xaxis_title='Date',
                yaxis_title='Price (₹)',
                yaxis2=dict(
                    title='Volume',
                    titlefont=dict(color='rgba(0, 0, 0, 0.5)'),
                    tickfont=dict(color='rgba(0, 0, 0, 0.5)'),
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=500,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with returns_tab:
            # Returns chart
            fig = go.Figure()
            
            if stock_data is not None and not stock_data.empty:
                fig.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Cumulative_Return'] * 100,
                    mode='lines',
                    name='Cumulative Return',
                    line=dict(color='#4CAF50', width=2)
                ))
                
                # Add daily returns as a subplot
                fig.add_trace(go.Bar(
                    x=stock_data.index,
                    y=stock_data['Daily_Return'] * 100,
                    name='Daily Return',
                    marker=dict(
                        color=stock_data['Daily_Return'].apply(
                            lambda x: 'rgba(76, 175, 80, 0.7)' if x >= 0 else 'rgba(244, 67, 54, 0.7)'
                        )
                    ),
                    yaxis='y2'
                ))
            else:
                # Add empty trace with a message
                fig.add_annotation(
                    x=0.5, y=0.5,
                    text="No data available",
                    showarrow=False,
                    font=dict(size=20)
                )
            
            fig.update_layout(
                title=f"{ticker} Returns",
                xaxis_title='Date',
                yaxis_title='Cumulative Return (%)',
                yaxis2=dict(
                    title='Daily Return (%)',
                    titlefont=dict(color='rgba(0, 0, 0, 0.5)'),
                    tickfont=dict(color='rgba(0, 0, 0, 0.5)'),
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=500,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Volatility chart
        st.subheader("Volatility Analysis")
        
        fig = go.Figure()
        
        if stock_data is not None and not stock_data.empty and 'Volatility' in stock_data.columns:
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Volatility'] * 100,
                mode='lines',
                name='Rolling Volatility (20-day)',
                line=dict(color='#FF9800', width=2)
            ))
        else:
            # Add empty trace with a message
            fig.add_annotation(
                x=0.5, y=0.5,
                text="No volatility data available",
                showarrow=False,
                font=dict(size=20)
            )
        
        fig.update_layout(
            title=f"{ticker} Historical Volatility",
            xaxis_title='Date',
            yaxis_title='Annualized Volatility (%)',
            height=300,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Company info and news
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Company information
            st.subheader("Company Information")
            
            if stock_info is not None:
                sector = stock_info.get('sector', 'N/A')
                industry = stock_info.get('industry', 'N/A')
                website = stock_info.get('website', '#')
                summary = stock_info.get('longBusinessSummary', 'No business summary available')
                
                st.markdown(f"""
                **Sector:** {sector}  
                **Industry:** {industry}  
                **Website:** [{website}]({website}) 
                
                **Business Summary:**  
                {summary}
                """)
            else:
                st.info("No company information available for this ticker.")
        
        with col2:
            # Financial metrics
            st.subheader("Key Metrics")
            
            if stock_info is not None:
                market_cap = stock_info.get('marketCap', 0)
                forward_pe = stock_info.get('forwardPE', None)
                dividend_yield = stock_info.get('dividendYield', None)
                
                metrics_df = pd.DataFrame({
                    'Metric': [
                        'Market Cap',
                        'Forward P/E',
                        'Dividend Yield'
                    ],
                    'Value': [
                        f"₹{market_cap / 1_000_000_000:.2f}B" if market_cap > 0 else "N/A",
                        f"{forward_pe:.2f}" if forward_pe else "N/A",
                        f"{dividend_yield:.2f}%" if dividend_yield else "N/A"
                    ]
                })
                
                st.table(metrics_df)
            else:
                st.info("No financial metrics available for this ticker.")
        
        # News and sentiment
        st.subheader("Recent News & Sentiment")
        
        news_items = fetch_financial_news(ticker, days=30, max_results=10)
        
        if news_items:
            # Analyze sentiment
            sentiment_analysis = analyze_news_sentiment(news_items)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Sentiment gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=sentiment_analysis['avg_sentiment'] * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Sentiment Score"},
                    gauge={
                        'axis': {'range': [-100, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [-100, -5], 'color': "red"},
                            {'range': [-5, 5], 'color': "gray"},
                            {'range': [5, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': sentiment_analysis['avg_sentiment'] * 100
                        }
                    }
                ))
                
                fig.update_layout(
                    height=250,
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Sentiment distribution
                dist_df = pd.DataFrame({
                    'Sentiment': list(sentiment_analysis['sentiment_distribution'].keys()),
                    'Percentage': list(sentiment_analysis['sentiment_distribution'].values())
                })
                
                fig = px.pie(
                    dist_df,
                    values='Percentage',
                    names='Sentiment',
                    title='Sentiment Distribution',
                    color='Sentiment',
                    color_discrete_map={
                        'Positive': 'green',
                        'Neutral': 'gray',
                        'Negative': 'red'
                    }
                )
                
                fig.update_layout(
                    height=250,
                    margin=dict(l=20, r=20, t=30, b=20),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # News items
                for item in news_items:
                    st.markdown(
                        f"<div style='padding:10px; margin-bottom:10px; border-left:3px solid {item['sentiment_color']}; background-color:rgba(0,0,0,0.02);'>"
                        f"<h4 style='margin:0; padding:0;'>{item['title']}</h4>"
                        f"<p style='margin:5px 0; font-size:0.8em; color:gray;'>{item['source']} | {item['date']}</p>"
                        f"<p style='margin:0; color:{item['sentiment_color']};'>Sentiment: {item['sentiment']} ({item['sentiment_score']:.2f})</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
        else:
            st.info("No recent news available for this stock")
    else:
        st.error(f"Unable to fetch data for ticker: {ticker}. Please enter a valid ticker symbol.")
