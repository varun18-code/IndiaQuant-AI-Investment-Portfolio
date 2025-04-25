import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import textwrap
from datetime import datetime, timedelta
from utils.portfolio import load_portfolio, get_sample_portfolio
from utils.stock_data import get_market_indices, get_stock_data
from utils.performance_metrics import calculate_performance_metrics, calculate_sector_allocation
from utils.sentiment_analysis import fetch_financial_news, analyze_news_sentiment
from utils.currency import convert_usd_to_inr, format_currency, format_market_cap, get_inr_symbol
from utils.alternative_data import get_alternative_data
import yfinance as yf # Added yfinance import

# Helper function to create explanations for financial terms
def get_term_explanation(term):
    explanations = {
        "Portfolio Value": "The total current market value of all investments held in your portfolio, including stocks and mutual funds.",
        "Daily Change": "The change in total portfolio value since the previous trading day, shown in both absolute value and percentage.",
        "YTD Return": "Year-to-Date Return shows how your portfolio has performed since January 1st of the current year.",
        "Sharpe Ratio": "A measure of risk-adjusted return. A higher ratio indicates better return relative to the risk taken.",
        "Sortino Ratio": "Similar to Sharpe ratio but only considers 'downside' risk or negative volatility.",
        "Max Drawdown": "The maximum observed loss from a peak to a trough before a new peak is attained.",
        "Volatility": "A statistical measure of the dispersion of returns for your investments, indicating risk level.",
        "Alpha": "Excess return of an investment relative to the return of a benchmark index.",
        "Beta": "Measure of a portfolio's volatility compared to the overall market. A beta > 1 means higher volatility.",
        "Sector Allocation": "Percentage breakdown of your investments across different industry sectors.",
        "NIFTY 50": "Benchmark Indian stock market index representing 50 of the largest companies listed on NSE.",
        "SENSEX": "Benchmark index of BSE composed of 30 of the largest and most actively traded stocks.",
        "BANK NIFTY": "Index of the most liquid and large-capitalized Indian banking stocks.",
        "NIFTY IT": "Index representing the performance of top IT companies listed on the NSE.",
        "NIFTY MIDCAP 100": "Index representing the performance of mid-sized companies in the Indian market."
    }
    return explanations.get(term, "")

# Function to create a metric with explanation tooltip
def create_metric_with_tooltip(label, value, delta=None, tooltip_text=None):
    # Determine delta class
    if delta is None:
        delta_class = "neutral-delta"
        delta_text = ""
    else:
        if isinstance(delta, str):
            delta_value = float(delta.replace('%', '').replace('+', '').replace('₹', '').strip())
        else:
            delta_value = delta

        delta_class = "positive-delta" if delta_value >= 0 else "negative-delta"
        delta_sign = "+" if delta_value > 0 else ""

        if isinstance(delta, str):
            delta_text = delta
        else:
            delta_text = f"{delta_sign}{delta:.2f}%"

    # Create tooltip if explanation exists
    tooltip_html = ""
    if tooltip_text:
        tooltip_html = f"""
        <div class="tooltip">ℹ️
            <span class="tooltiptext">{tooltip_text}</span>
        </div>
        """

    # Generate HTML for metric
    metric_html = f"""
    <div class="card">
        <div class="metric-label">{label} {tooltip_html}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-delta {delta_class}">{delta_text}</div>
    </div>
    """
    return metric_html

def show():
    """Display the dashboard page"""
    # Custom styling for better UI
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.0em;
            font-weight: 600;
            background: linear-gradient(90deg, #1E3A8A, #3B82F6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.8em;
        }

        .section-header {
            font-size: 1.3em;
            font-weight: 600;
            color: #1E3A8A;
            margin: 20px 0 15px 0;
            border-bottom: 2px solid #EFF6FF;
            padding-bottom: 5px;
        }

        .card {
            border-radius: 10px;
            padding: 20px;
            background-color: white;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            border: 1px solid #E5E7EB;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        }

        .metric-label {
            font-size: 0.9em;
            color: #6B7280;
            margin-bottom: 0.2em;
            display: flex;
            align-items: center;
        }

        .info-icon {
            margin-left: 5px;
            color: #3B82F6;
            cursor: help;
        }

        .metric-value {
            font-size: 1.7em;
            font-weight: 600;
            margin-bottom: 0.1em;
            color: #111827;
        }

        .metric-delta {
            font-size: 0.9em;
            font-weight: 500;
            padding: 2px 6px;
            border-radius: 4px;
            display: inline-block;
        }

        .positive-delta {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10B981;
        }

        .negative-delta {
            background-color: rgba(239, 68, 68, 0.1);
            color: #EF4444;
        }

        .neutral-delta {
            background-color: rgba(156, 163, 175, 0.1);
            color: #6B7280;
        }

        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
            margin-left: 5px;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 250px;
            background-color: #F3F4F6;
            color: #1F2937;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            font-size: 0.8em;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -125px;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            border: 1px solid #E5E7EB;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        .infobox {
            background-color: #EFF6FF;
            border-left: 4px solid #3B82F6;
            padding: 12px 15px;
            margin: 15px 0;
            border-radius: 4px;
            font-size: 0.9em;
            color: #1E3A8A;
        }

        .chart-container {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            border: 1px solid #E5E7EB;
        }

        .small-text {
            font-size: 0.8em;
            color: #6B7280;
        }

        .insights-header {
            font-size: 1.2em;
            color: #3B82F6;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }

        .insights-header:before {
            content: "💡";
            margin-right: 8px;
        }

        .market-pill {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            margin-right: 5px;
        }

        .market-up {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .market-down {
            background-color: rgba(239, 68, 68, 0.1);
            color: #EF4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .market-neutral {
            background-color: rgba(156, 163, 175, 0.1);
            color: #6B7280;
            border: 1px solid rgba(156, 163, 175, 0.3);
        }

        .news-card {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 6px;
            background-color: #F9FAFB;
            border-left: 3px solid #3B82F6;
            transition: transform 0.2s;
        }

        .news-card:hover {
            transform: translateX(5px);
        }

        .news-title {
            font-weight: 600;
            margin-bottom: 5px;
            color: #1F2937;
            font-size: 0.95em;
        }

        .news-meta {
            font-size: 0.8em;
            color: #6B7280;
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }

        .news-sentiment {
            font-size: 0.8em;
            font-weight: 500;
            padding: 2px 6px;
            border-radius: 4px;
            display: inline-block;
        }

        .metric-explainer {
            font-size: 0.8em;
            color: #6B7280;
            margin-top: 5px;
            font-style: italic;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            border-radius: 5px 5px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }

        .stTabs [aria-selected="true"] {
            background-color: #EFF6FF;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # Dashboard header with greeting based on time of day
    current_hour = datetime.now().hour
    greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 17 else "Good evening"

    st.markdown(f'<div class="main-header">{greeting} - Your Portfolio Dashboard</div>', unsafe_allow_html=True)

    # Information box explaining the dashboard
    st.markdown("""
    <div class="infobox">
        <strong>Welcome to your IndiaQuant Dashboard!</strong> Here you can see your portfolio at a glance, market indices, key financial metrics, 
        and AI-generated insights. Hover over any metric to learn more about what it means.
    </div>
    """, unsafe_allow_html=True)

    # Check if we have a portfolio, if not create a sample one
    portfolio = load_portfolio()
    if not portfolio.holdings:
        portfolio = get_sample_portfolio()

    # Get portfolio value and metrics
    portfolio_value = portfolio.get_portfolio_value()

    # Convert values to INR
    inr_total_value = convert_usd_to_inr(portfolio_value['total_value'])

    # Enhanced portfolio summary metrics with mutual fund integration
    portfolio_returns = portfolio.get_portfolio_returns(period='1y')

    # Get benchmark data
    indices = get_market_indices()
    nifty_data = indices.get('NIFTY 50')

    # Calculate relevant performance metrics if data is available
    if portfolio_returns is not None and nifty_data is not None:
        nifty_returns = nifty_data['Close'].pct_change().dropna()
        aligned_portfolio_returns = portfolio_returns['Portfolio_Daily_Return'].reindex(nifty_returns.index).dropna()
        aligned_nifty_returns = nifty_returns.reindex(aligned_portfolio_returns.index)
        performance_metrics = calculate_performance_metrics(
            aligned_portfolio_returns, 
            aligned_nifty_returns
        )
    else:
        performance_metrics = {"total_return": 0, "alpha": 0, "sharpe_ratio": 0, "beta": 0}

    # Count the stock and mutual fund positions
    stock_positions = len(portfolio_value['positions'])
    mutual_fund_positions = len(portfolio_value.get('mutual_fund_positions', []))
    total_positions = stock_positions + mutual_fund_positions

    # Create rows of metrics with better visualization
    col1, col2, col3 = st.columns(3)

    with col1:
        # Add a more visually appealing metric with custom styling
        total_value = inr_total_value
        gain_loss_pct = portfolio_value['total_gain_loss_pct']
        gain_loss_color = "green" if gain_loss_pct >= 0 else "red"
        gain_loss_arrow = "↑" if gain_loss_pct >= 0 else "↓"
        gain_loss_prefix = "+" if gain_loss_pct >= 0 else ""

        st.markdown(
            f"""
            <div style="border:1px solid #f0f2f6; border-radius:10px; padding:20px; text-align:center; 
                 background-color:rgba(76, 175, 80, 0.05);">
                <h3 style="margin-bottom:0px; font-size:1rem; color:#555;">Total Portfolio Value</h3>
                <h2 style="margin:10px 0; font-size:2rem; color:#333;">{format_currency(total_value)}</h2>
                <p style="color:{gain_loss_color}; font-weight:bold; font-size:1.1rem;">
                    {gain_loss_arrow} {gain_loss_prefix}{gain_loss_pct:.2f}%
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    with col2:
        # Asset allocation visual
        st.markdown(
            f"""
            <div style="border:1px solid #f0f2f6; border-radius:10px; padding:20px; text-align:center;
                 background-color:rgba(33, 150, 243, 0.05);">
                <h3 style="margin-bottom:0px; font-size:1rem; color:#555;">Asset Allocation</h3>
                <div style="display:flex; justify-content:space-around; margin-top:15px;">
                    <div>
                        <h4 style="margin:0; color:#333; font-size:0.9rem;">Stocks</h4>
                        <h2 style="margin:5px 0; color:#1976D2;">{stock_positions}</h2>
                    </div>
                    <div>
                        <h4 style="margin:0; color:#333; font-size:0.9rem;">Mutual Funds</h4>
                        <h2 style="margin:5px 0; color:#673AB7;">{mutual_fund_positions}</h2>
                    </div>
                </div>
                <p style="margin-top:10px;">Total: {total_positions} investments</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    with col3:
        # Market Insight
        current_date = datetime.now()
        day_of_week = current_date.strftime('%A')
        is_weekend = day_of_week in ['Saturday', 'Sunday']

        market_status = "Closed" if is_weekend else "Open"
        market_color = "#F44336" if is_weekend else "#4CAF50"

        current_time_ist = (datetime.now() + timedelta(hours=5, minutes=30)).strftime("%H:%M")

        st.markdown(
            f"""
            <div style="border:1px solid #f0f2f6; border-radius:10px; padding:20px; text-align:center;
                 background-color:rgba(255, 193, 7, 0.05);">
                <h3 style="margin-bottom:0px; font-size:1rem; color:#555;">Indian Market Status</h3>
                <h2 style="margin:10px 0; font-size:1.5rem; color:{market_color};">{market_status}</h2>
                <p>NSE/BSE: 9:15 - 15:30 IST</p>
                <p>Current time (IST): {current_time_ist}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Second row of metrics - Performance metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        # YTD Return with enhanced styling
        st.markdown(
            f"""
            <div style="border:1px solid #f0f2f6; border-radius:10px; padding:15px; text-align:center;
                 background-color:rgba(255, 255, 255, 0.7);">
                <h3 style="margin-bottom:0px; font-size:0.9rem; color:#555;">YTD Return</h3>
                <h2 style="margin:10px 0; font-size:1.5rem; color:{'#4CAF50' if performance_metrics['total_return'] >= 0 else '#F44336'};">
                    {performance_metrics['total_return']:.2f}%
                </h2>
                <p style="font-size:0.8rem; color:#666;">Alpha: {performance_metrics['alpha']:.2f}%</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    with col2:
        # Sharpe Ratio with enhanced styling
        sharpe_color = "#4CAF50" if performance_metrics['sharpe_ratio'] >= 1 else "#FF9800" if performance_metrics['sharpe_ratio'] >= 0 else "#F44336"
        sharpe_text = "Excellent" if performance_metrics['sharpe_ratio'] >= 1.5 else "Good" if performance_metrics['sharpe_ratio'] >= 1 else "Average" if performance_metrics['sharpe_ratio'] >= 0 else "Poor"

        st.markdown(
            f"""
            <div style="border:1px solid #f0f2f6; border-radius:10px; padding:15px; text-align:center;
                 background-color:rgba(255, 255, 255, 0.7);">
                <h3 style="margin-bottom:0px; font-size:0.9rem; color:#555;">Sharpe Ratio</h3>
                <h2 style="margin:10px 0; font-size:1.5rem; color:{sharpe_color};">
                    {performance_metrics['sharpe_ratio']:.2f}
                </h2>
                <p style="font-size:0.8rem; color:#666;">Risk-adjusted return: {sharpe_text}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    with col3:
        # Beta with enhanced styling
        beta_color = "#4CAF50" if 0.8 <= performance_metrics['beta'] <= 1.2 else "#FF9800" if performance_metrics['beta'] < 0.8 else "#F44336"
        beta_text = "Market neutral" if 0.8 <= performance_metrics['beta'] <= 1.2 else "Defensive" if performance_metrics['beta'] < 0.8 else "Aggressive"

        st.markdown(
            f"""
            <div style="border:1px solid #f0f2f6; border-radius:10px; padding:15px; text-align:center;
                 background-color:rgba(255, 255, 255, 0.7);">
                <h3 style="margin-bottom:0px; font-size:0.9rem; color:#555;">Beta to NIFTY 50</h3>
                <h2 style="margin:10px 0; font-size:1.5rem; color:{beta_color};">
                    {performance_metrics['beta']:.2f}
                </h2>
                <p style="font-size:0.8rem; color:#666;">Market sensitivity: {beta_text}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Portfolio Performance Chart
    st.subheader("Portfolio Performance")

    if portfolio_returns is not None and not portfolio_returns.empty:
        # Plot portfolio cumulative returns
        fig = go.Figure()

        # Portfolio returns
        fig.add_trace(go.Scatter(
            x=portfolio_returns.index,
            y=portfolio_returns['Portfolio_Cumulative_Return'] * 100,
            mode='lines',
            name='Portfolio',
            line=dict(color='#1E88E5', width=2)
        ))

        # NIFTY 50 returns if available
        if nifty_data is not None and 'Close' in nifty_data.columns and len(nifty_data) > 1:
            # Calculate NIFTY returns properly
            nifty_returns = nifty_data['Close'].pct_change().dropna()

            if not nifty_returns.empty:
                nifty_cumulative_returns = (1 + nifty_returns).cumprod() - 1
                fig.add_trace(go.Scatter(
                    x=nifty_cumulative_returns.index,
                    y=nifty_cumulative_returns * 100,
                    mode='lines',
                    name='NIFTY 50',
                    line=dict(color='#FFC107', width=1.5, dash='dash')
                ))

        fig.update_layout(
            title='Cumulative Returns (%)',
            xaxis_title='Date',
            yaxis_title='Return (%)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=400,
            margin=dict(l=0, r=0, t=30, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough portfolio data to display performance chart")

    # Portfolio Allocation and Recent Activity
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Portfolio Allocation")
        sector_allocation = calculate_sector_allocation(portfolio_value)

        if sector_allocation['sectors']:
            # Create a pie chart
            fig = px.pie(
                names=sector_allocation['sectors'],
                values=sector_allocation['weights'],
                title='Sector Allocation'
            )

            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#FFFFFF', width=1))
            )

            fig.update_layout(
                showlegend=False,
                height=300,
                margin=dict(l=0, r=0, t=30, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No portfolio allocation data available")

    with col2:
        st.subheader("Top Holdings")

        # Gather all positions (stocks + mutual funds)
        all_positions = []

        # Add stock positions
        if portfolio_value['positions']:
            for pos in portfolio_value['positions']:
                all_positions.append({
                    'name': pos['ticker'],
                    'value': convert_usd_to_inr(pos['current_value']),
                    'gain_loss_pct': pos['gain_loss_pct'],
                    'type': 'Stock'
                })

        # Add mutual fund positions
        if portfolio_value.get('mutual_fund_positions', []):
            for mf in portfolio_value['mutual_fund_positions']:
                fund_name = mf.get('fund_name', mf['ticker'])
                # Truncate fund name if too long
                if len(fund_name) > 25:
                    fund_name = fund_name[:22] + "..."

                all_positions.append({
                    'name': fund_name,
                    'value': convert_usd_to_inr(mf['current_value']),
                    'gain_loss_pct': mf['gain_loss_pct'],
                    'type': 'Fund'
                })

        if all_positions:
            # Get top 5 positions by value
            top_positions = sorted(all_positions, key=lambda x: x['value'], reverse=True)[:5]

            # Create a visually enhanced table with conditional formatting and badges
            for idx, pos in enumerate(top_positions):
                gain_color = "#4CAF50" if pos['gain_loss_pct'] >= 0 else "#F44336"
                gain_arrow = "↑" if pos['gain_loss_pct'] >= 0 else "↓"
                gain_prefix = "+" if pos['gain_loss_pct'] >= 0 else ""
                pos_type = pos['type']
                type_color = "#1976D2" if pos_type == 'Stock' else "#673AB7"

                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; padding:10px 15px; margin-bottom:8px; 
                        border-radius:5px; background-color:rgba(240, 242, 246, 0.4); border-left:4px solid {type_color};">
                        <div style="font-weight:bold; flex-grow:1;">{pos['name']}</div>
                        <div style="display:flex; flex-direction:column; align-items:flex-end; min-width:120px;">
                            <div style="font-weight:bold;">{format_currency(pos['value'])}</div>
                            <div style="display:flex; align-items:center;">
                                <span style="font-size:0.8rem; color:{gain_color}; margin-right:5px;">
                                    {gain_arrow} {gain_prefix}{pos['gain_loss_pct']:.2f}%
                                </span>
                                <span style="font-size:0.7rem; background-color:{type_color}; color:white; 
                                    padding:2px 5px; border-radius:3px;">{pos_type}</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No holdings data available. Add investments from the Portfolio Management page.")

    # Market Overview
    st.subheader("Market Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Market indices
        indices = get_market_indices()

        if indices:
            # Prepare data for display
            index_data = []
            for name, data in indices.items():
                if data is not None and not data.empty and len(data) >= 2:
                    current_price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
                    daily_change = (current_price / prev_price - 1) * 100 if prev_price != 0 else 0

                    index_data.append({
                        'Index': name,
                        'Price': current_price,
                        'Change': daily_change
                    })

            if index_data:
                df = pd.DataFrame(index_data)
                # Indian indices are already in INR, no need to convert
                df['Price'] = df['Price'].map(lambda x: f"₹{x:,.2f}")
                df['Change'] = df['Change'].map(lambda x: f"{x:+.2f}%")

                st.table(df)
        else:
            st.info("No market data available")

    with col2:
        # Latest Indian market news and insights
        st.markdown('<div class="insights-header">Indian Market Insights</div>', unsafe_allow_html=True)

        # Get some tickers for Indian market news
        indian_tickers = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
        ticker_choice = indian_tickers[0] if indian_tickers else 'RELIANCE.NS'

        news = fetch_financial_news(ticker_choice, days=3, max_results=5)

        # Indian market specific insights - current market factors
        current_month = datetime.now().month
        current_festival = ""

        if current_month == 3:
            current_festival = "🎭 Financial Year End - Watch for last-minute corporate actions"
        elif current_month == 4:
            current_festival = "✨ New Financial Year - Budget impacts coming into effect"
        elif current_month == 8:
            current_festival = "🪔 Approaching Festival Season - Retail and consumer stocks may see momentum"
        elif current_month == 10 or current_month == 11:
            current_festival = "🪔 Diwali Season - Traditionally bullish for Indian markets"

        # Display the festival insight if available
        if current_festival:
            st.markdown(f"<div class='card'>{current_festival}</div>", unsafe_allow_html=True)

        # Indian Market Specific Data Points
        try:
            # Try to get FII/DII data (simulated here)
            today = datetime.now().strftime('%Y-%m-%d')
            st.markdown(
                f"<div class='card'>"
                f"<b>FII/DII Flows</b> ({today})<br>"
                f"<span style='color:{'red'};'>FII: ₹-1,245.32 Cr</span> | "
                f"<span style='color:{'green'};'>DII: ₹1,667.45 Cr</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        except:
            pass

        # Display news if available
        if news:
            for item in news[:2]:
                st.markdown(
                    f"<div style='padding:5px 0;'>"
                    f"<span style='color:{item['sentiment_color']};'>{'↑' if item['sentiment_score'] > 0 else '↓' if item['sentiment_score'] < 0 else '→'}</span> "
                    f"<span style='font-size:0.9em;'>{textwrap.shorten(item['title'], width=60, placeholder='...')}</span><br>"
                    f"<span style='font-size:0.7em; color:gray;'>{item['source']} - {item['date']}</span>"                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No news data available")

    # Alternative Data Insights
    st.subheader("Alternative Data Insights")

    # Create a sample ticker for alternative data (using Reliance Industries)
    alt_data_ticker = 'RELIANCE.NS'

    # If we have a portfolio, use the largest holding
    if portfolio_value['positions']:
        top_position = sorted(portfolio_value['positions'], key=lambda x: x['current_value'], reverse=True)[0]
        alt_data_ticker = top_position['ticker']

    alternative_data = get_alternative_data(alt_data_ticker)

    if alternative_data:
        col1, col2, col3 = st.columns(3)

        with col1:
            sat_data = alternative_data['satellite_data']
            st.markdown(
                f"<div style='border:1px solid #f0f0f0; padding:10px; border-radius:5px;'>"
                f"<h5>{sat_data['metric_name']}</h5>"
                f"<p style='font-size:1.5em;'>{sat_data['current_value']:.1f}</p>"
                f"<p>Weekly change: <span style='color:{'green' if sat_data['weekly_change_pct'] > 0 else 'red'}'>{'↑' if sat_data['weekly_change_pct'] > 0 else '↓'} {abs(sat_data['weekly_change_pct']):.1f}%</span></p>"
                f"<p style='font-size:0.8em;'>{sat_data['insight']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )

        with col2:
            ship_data = alternative_data['shipping_data']
            st.markdown(
                f"<div style='border:1px solid #f0f0f0; padding:10px; border-radius:5px;'>"
                f"<h5>Global Shipping Congestion</h5>"
                f"<p style='font-size:1.5em;'>{ship_data['current_congestion']:.1f}%</p>"
                f"<p>Weekly change: <span style='color:{'red' if ship_data['weekly_change_pct'] > 0 else 'green'}'>{'↑' if ship_data['weekly_change_pct'] > 0 else '↓'} {abs(ship_data['weekly_change_pct']):.1f}%</span></p>"
                f"<p style='font-size:0.8em;'>{ship_data['insight']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )

        with col3:
            spend_data = alternative_data['spending_data']
            st.markdown(
                f"<div style='border:1px solid #f0f0f0; padding:10px; border-radius:5px;'>"
                f"<h5>Consumer Spending ({spend_data['category']})</h5>"
                f"<p style='font-size:1.5em;'>{spend_data['current_spending_avg']:.1f}</p>"
                f"<p>Weekly change: <span style='color:{'green' if spend_data['weekly_change_pct'] > 0 else 'red'}'>{'↑' if spend_data['weekly_change_pct'] > 0 else '↓'} {abs(spend_data['weekly_change_pct']):.1f}%</span></p>"
                f"<p style='font-size:0.8em;'>{spend_data['insight']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )