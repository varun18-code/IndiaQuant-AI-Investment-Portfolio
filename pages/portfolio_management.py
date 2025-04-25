import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import base64
from utils.portfolio import load_portfolio, save_portfolio, get_sample_portfolio
from utils.stock_data import get_stock_data, get_stock_info
from utils.performance_metrics import calculate_performance_metrics, calculate_sector_allocation, calculate_risk_metrics
from utils.social_sharing import (
    generate_text_summary, 
    generate_performance_image,
    generate_allocation_image,
    generate_shareable_portfolio_card,
    get_share_links,
    generate_qr_code,
    get_image_download_link
)

def show():
    """Display the portfolio management page"""
    st.header("Portfolio Management")
    
    # Check if we have a portfolio, if not create a sample one
    portfolio = load_portfolio()
    if not portfolio.holdings:
        if st.button("Load Sample Portfolio"):
            portfolio = get_sample_portfolio()
            save_portfolio(portfolio)
            st.success("Sample portfolio loaded!")
            st.rerun()
    
    # Get portfolio value and metrics
    portfolio_value = portfolio.get_portfolio_value()
    
    # Portfolio Summary
    st.subheader("Portfolio Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Value",
            value=f"₹{portfolio_value['total_value']:,.2f}",
            delta=f"{portfolio_value['total_gain_loss_pct']:.2f}%"
        )
    
    with col2:
        st.metric(
            label="Total Cost",
            value=f"₹{portfolio_value['total_cost']:,.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Gain/Loss",
            value=f"₹{portfolio_value['total_gain_loss']:,.2f}",
            delta=None
        )
    
    with col4:
        # Number of positions
        st.metric(
            label="Positions",
            value=len(portfolio_value['positions']),
            delta=None
        )
    
    # Portfolio Holdings Table
    st.subheader("Portfolio Holdings")
    
    if portfolio_value['positions']:
        # Prepare data for the table
        data = []
        for pos in portfolio_value['positions']:
            data.append({
                'Ticker': pos['ticker'],
                'Shares': pos['shares'],
                'Avg Price': f"₹{pos['avg_price']:.2f}",
                'Current Price': f"₹{pos['current_price']:.2f}",
                'Cost Basis': f"₹{pos['cost_basis']:.2f}",
                'Market Value': f"₹{pos['current_value']:.2f}",
                'Gain/Loss': f"₹{pos['gain_loss']:.2f}",
                'Gain/Loss %': f"{pos['gain_loss_pct']:.2f}%"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No holdings in portfolio. Add positions or load a sample portfolio.")
    
    # Portfolio Management
    st.subheader("Manage Portfolio", help="Add or remove stocks and mutual funds from your portfolio")
    
    # Modern tabs with icons for better UX
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 View Holdings", 
        "➕ Add Stock", 
        "🔄 Remove Stock", 
        "💹 Mutual Funds",
        "📊 Share"
    ])
    
    # Tab 1: View holdings with improved visualization
    with tab1:
        # Improved holdings visualization
        st.write("### Your Investment Holdings")
        
        # Create tabs to separate stocks and mutual funds for better organization
        stock_tab, mf_tab = st.tabs(["Stocks", "Mutual Funds"])
        
        with stock_tab:
            if portfolio_value['positions']:
                # Create a more visually appealing table with conditional formatting
                data = []
                for pos in portfolio_value['positions']:
                    # Conditional color formatting
                    gain_color = "green" if pos['gain_loss'] > 0 else "red"
                    gain_arrow = "↑" if pos['gain_loss'] > 0 else "↓"
                    
                    data.append({
                        'Ticker': pos['ticker'],
                        'Shares': f"{pos['shares']:.2f}",
                        'Avg Price': f"₹{pos['avg_price']:.2f}",
                        'Current Price': f"₹{pos['current_price']:.2f}",
                        'Market Value': f"₹{pos['current_value']:,.2f}",
                        'Gain/Loss': f"<span style='color:{gain_color}'>₹{pos['gain_loss']:,.2f} {gain_arrow}</span>",
                        'Gain/Loss %': f"<span style='color:{gain_color}'>{pos['gain_loss_pct']:.2f}% {gain_arrow}</span>"
                    })
                
                df = pd.DataFrame(data)
                
                # Use a custom formatter for the table
                st.markdown(
                    """
                    <style>
                    .stock-table {
                        font-size: 0.9rem;
                        width: 100%;
                    }
                    .stock-table thead {
                        background-color: #f0f2f6;
                    }
                    .stock-table th {
                        text-align: left;
                        padding: 8px;
                    }
                    .stock-table td {
                        padding: 8px;
                        border-bottom: 1px solid #e6e9ef;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                # Display the dataframe with styled HTML
                st.write(df.to_html(escape=False, classes='stock-table'), unsafe_allow_html=True)
                
                # Show a pie chart of the allocation
                st.write("#### Stock Allocation")
                fig = px.pie(
                    values=[pos['current_value'] for pos in portfolio_value['positions']],
                    names=[pos['ticker'] for pos in portfolio_value['positions']],
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig.update_layout(
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=400
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No stock holdings in your portfolio. Add positions or load a sample portfolio.")
        
        with mf_tab:
            if hasattr(portfolio, 'mutual_funds') and portfolio.mutual_funds:
                # Get the mutual fund positions
                mutual_fund_positions = portfolio_value.get('mutual_fund_positions', [])
                
                if mutual_fund_positions:
                    # Create a visually appealing table with conditional formatting
                    data = []
                    for mf in mutual_fund_positions:
                        # Conditional color formatting
                        gain_color = "green" if mf['gain_loss'] > 0 else "red"
                        gain_arrow = "↑" if mf['gain_loss'] > 0 else "↓"
                        
                        fund_display_name = mf.get('fund_name', mf['ticker'])
                        
                        data.append({
                            'Fund': fund_display_name,
                            'Units': f"{mf['units']:.2f}",
                            'Purchase NAV': f"₹{mf['avg_nav']:.2f}",
                            'Current NAV': f"₹{mf['current_nav']:.2f}",
                            'Current Value': f"₹{mf['current_value']:,.2f}",
                            'Gain/Loss': f"<span style='color:{gain_color}'>₹{mf['gain_loss']:,.2f} {gain_arrow}</span>",
                            'Gain/Loss %': f"<span style='color:{gain_color}'>{mf['gain_loss_pct']:.2f}% {gain_arrow}</span>"
                        })
                    
                    df = pd.DataFrame(data)
                    
                    # Display the dataframe with styled HTML
                    st.write(df.to_html(escape=False, classes='stock-table'), unsafe_allow_html=True)
                    
                    # Show a pie chart of the mutual fund allocation
                    st.write("#### Mutual Fund Allocation")
                    fig = px.pie(
                        values=[mf['current_value'] for mf in mutual_fund_positions],
                        names=[mf.get('fund_name', mf['ticker']) for mf in mutual_fund_positions],
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_layout(
                        margin=dict(t=20, b=20, l=20, r=20),
                        height=400
                    )
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No mutual fund holdings in your portfolio. Add mutual funds from the 'Mutual Funds' tab.")
            else:
                st.info("No mutual fund holdings in your portfolio. Add mutual funds from the 'Mutual Funds' tab.")
    
    # Tab 2: Enhanced Add Stock Position
    with tab2:
        # Add position form with improved UX
        st.write("### Add New Stock Position")
        
        with st.form("add_position_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(
                    """
                    <div style="border-left: 4px solid #1E88E5; padding-left: 10px;">
                    <p style="color: #1E88E5; font-size: 1.2rem; margin-bottom: 5px;">Stock Details</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                ticker = st.text_input("Ticker Symbol (append .NS for NSE stocks)", 
                                     value="", 
                                     help="For NSE stocks, append .NS (e.g., RELIANCE.NS). For BSE, append .BO").upper()
                shares = st.number_input("Number of Shares", min_value=0.01, value=1.0, step=0.01)
            
            with col2:
                st.markdown(
                    """
                    <div style="border-left: 4px solid #FFC107; padding-left: 10px;">
                    <p style="color: #FFC107; font-size: 1.2rem; margin-bottom: 5px;">Transaction Details</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                purchase_price = st.number_input("Purchase Price per Share (₹)", min_value=0.01, value=100.0, step=0.01)
                purchase_date = st.date_input("Purchase Date", value=datetime.now())
            
            # Add a checkbox for SIP (for future enhancement)
            is_sip = st.checkbox("This is a Systematic Investment Plan (SIP)", 
                               help="Check if this is a recurring investment. Future versions will support automatic SIP tracking.")
            
            col_submit, _ = st.columns([1, 3])
            with col_submit:
                submitted = st.form_submit_button("Add to Portfolio", 
                                              help="Add this stock to your portfolio",
                                              use_container_width=True)
            
            if submitted:
                if ticker and shares > 0 and purchase_price > 0:
                    # Add .NS suffix if not present for Indian stocks
                    if '.' not in ticker:
                        ticker = ticker + '.NS'
                    
                    # Check if ticker is valid
                    stock_data = get_stock_data(ticker, period='1d')
                    if stock_data is not None and not stock_data.empty:
                        portfolio.add_position(
                            ticker,
                            shares,
                            purchase_price,
                            purchase_date.strftime('%Y-%m-%d')
                        )
                        save_portfolio(portfolio)
                        st.success(f"✅ Successfully added {shares} shares of {ticker} to portfolio!")
                        st.balloons()  # Add a visual celebration
                        st.rerun()
                    else:
                        st.error(f"❌ Invalid ticker symbol: {ticker}. Please verify the stock symbol.")
                else:
                    st.error("❌ Please fill in all fields with valid values")
        
        # Add a quick ticker search helper
        with st.expander("Need help finding a ticker symbol?"):
            st.write("Common Indian Stock Tickers:")
            
            indian_stocks = {
                "Reliance Industries": "RELIANCE.NS",
                "TCS": "TCS.NS",
                "HDFC Bank": "HDFCBANK.NS",
                "Infosys": "INFY.NS",
                "ICICI Bank": "ICICIBANK.NS",
                "HUL": "HINDUNILVR.NS",
                "Bajaj Finance": "BAJFINANCE.NS",
                "ITC": "ITC.NS",
                "Bharti Airtel": "BHARTIARTL.NS",
                "Larsen & Toubro": "LT.NS"
            }
            
            stock_list = pd.DataFrame({
                "Company": indian_stocks.keys(),
                "Ticker": indian_stocks.values()
            })
            
            st.table(stock_list)
    
    # Tab 3: Enhanced Remove Stock Position
    with tab3:
        st.write("### Sell/Remove Stock Position")
        
        with st.form("remove_position_form", clear_on_submit=True):
            # Create a list of tickers in the portfolio
            tickers = [pos['ticker'] for pos in portfolio_value['positions']]
            
            if tickers:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(
                        """
                        <div style="border-left: 4px solid #F44336; padding-left: 10px;">
                        <p style="color: #F44336; font-size: 1.2rem; margin-bottom: 5px;">Stock Selection</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    ticker_to_sell = st.selectbox("Select Position to Sell", tickers)
                    # Find the position
                    selected_position = next((pos for pos in portfolio_value['positions'] if pos['ticker'] == ticker_to_sell), None)
                    
                    if selected_position:
                        st.metric(
                            label="Current Market Price", 
                            value=f"₹{selected_position['current_price']:.2f}",
                            delta=f"{selected_position['gain_loss_pct']:.2f}%"
                        )
                        max_shares = selected_position['shares']
                        shares_to_sell = st.number_input("Number of Shares to Sell", 
                                                      min_value=0.01, 
                                                      max_value=float(max_shares), 
                                                      value=float(max_shares), 
                                                      step=0.01)
                
                with col2:
                    st.markdown(
                        """
                        <div style="border-left: 4px solid #4CAF50; padding-left: 10px;">
                        <p style="color: #4CAF50; font-size: 1.2rem; margin-bottom: 5px;">Transaction Details</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    current_price = selected_position['current_price'] if selected_position else 0
                    sell_price = st.number_input("Sell Price per Share (₹)", 
                                              min_value=0.01, 
                                              value=float(current_price), 
                                              step=0.01)
                    sell_date = st.date_input("Sell Date", value=datetime.now())
                    
                    # Calculate and display potential profit/loss
                    if selected_position:
                        potential_pl = (sell_price - selected_position['avg_price']) * shares_to_sell
                        pl_percent = (sell_price / selected_position['avg_price'] - 1) * 100
                        pl_color = "green" if potential_pl >= 0 else "red"
                        pl_prefix = "+" if potential_pl >= 0 else ""
                        
                        st.markdown(
                            f"""
                            <div style="background-color: {'rgba(76, 175, 80, 0.1)' if potential_pl >= 0 else 'rgba(244, 67, 54, 0.1)'}; 
                                  padding: 10px; border-radius: 5px; margin-top: 15px;">
                                <p style="font-weight: bold; margin-bottom: 5px;">Transaction Summary</p>
                                <p>Potential Profit/Loss: <span style="color: {pl_color}; font-weight: bold;">
                                  {pl_prefix}₹{potential_pl:.2f} ({pl_prefix}{pl_percent:.2f}%)</span></p>
                                <p>Total Sale Value: ₹{sell_price * shares_to_sell:.2f}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                col_submit, _ = st.columns([1, 3])
                with col_submit:
                    submitted = st.form_submit_button("Complete Sale", 
                                                  help="Sell shares from your portfolio",
                                                  use_container_width=True)
                
                if submitted:
                    if ticker_to_sell and shares_to_sell > 0 and sell_price > 0:
                        success = portfolio.remove_position(
                            ticker_to_sell,
                            shares_to_sell,
                            sell_price,
                            sell_date.strftime('%Y-%m-%d')
                        )
                        
                        if success:
                            save_portfolio(portfolio)
                            st.success(f"✅ Successfully sold {shares_to_sell} shares of {ticker_to_sell}!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to remove position. Please try again.")
                    else:
                        st.error("❌ Please fill in all fields with valid values")
            else:
                st.info("No positions in portfolio to sell. Add stocks from the 'Add Stock' tab first.")
                submitted = st.form_submit_button("Complete Sale", disabled=True)
    
    # Tab 4: Mutual Funds Management
    with tab4:
        st.write("### Mutual Fund Portfolio")
        
        # Create tabs for adding and redeeming mutual funds
        mf_add_tab, mf_redeem_tab = st.tabs(["Add Mutual Fund", "Redeem Mutual Fund"])
        
        with mf_add_tab:
            with st.form("add_mutual_fund_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(
                        """
                        <div style="border-left: 4px solid #673AB7; padding-left: 10px;">
                        <p style="color: #673AB7; font-size: 1.2rem; margin-bottom: 5px;">Fund Details</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    
                    # Dropdown for fund category
                    fund_category = st.selectbox(
                        "Fund Category",
                        [
                            "Equity - Large Cap",
                            "Equity - Mid Cap",
                            "Equity - Small Cap",
                            "Equity - ELSS (Tax Saving)",
                            "Hybrid - Balanced",
                            "Debt - Corporate Bond",
                            "Debt - Government Securities",
                            "Index Fund",
                            "International Fund",
                            "Sector Fund"
                        ]
                    )
                    
                    # Fund selection based on category (simplified for demo)
                    fund_options = {
                        "Equity - Large Cap": [
                            {"name": "HDFC Top 100 Fund - Direct Plan - Growth Option", "code": "INF179K01BB8"},
                            {"name": "ICICI Prudential Bluechip Fund - Direct Plan - Growth Option", "code": "INF209K01VL4"},
                            {"name": "Axis Bluechip Fund - Direct Plan - Growth Option", "code": "INF846K01JA0"}
                        ],
                        "Equity - Mid Cap": [
                            {"name": "Kotak Emerging Equity Fund - Direct Plan - Growth Option", "code": "INF174K01LM2"},
                            {"name": "SBI Magnum Midcap Fund - Direct Plan - Growth Option", "code": "INF200K01RQ7"}
                        ],
                        "Equity - ELSS (Tax Saving)": [
                            {"name": "Axis Long Term Equity Fund - Direct Plan - Growth Option", "code": "INF846K01PE0"},
                            {"name": "DSP Tax Saver Fund - Direct Plan - Growth Option", "code": "INF740K01367"}
                        ],
                        "Hybrid - Balanced": [
                            {"name": "SBI Equity Hybrid Fund - Direct Plan - Growth Option", "code": "INF109K01VK7"},
                            {"name": "ICICI Prudential Balanced Advantage Fund - Direct Plan - Growth Option", "code": "INF109K01VQ4"}
                        ],
                        "Debt - Corporate Bond": [
                            {"name": "Aditya Birla Sun Life Corporate Bond Fund - Direct Plan - Growth Option", "code": "INF090I01KJ8"},
                            {"name": "HDFC Corporate Bond Fund - Direct Plan - Growth Option", "code": "INF179K01BF9"}
                        ],
                        "Index Fund": [
                            {"name": "UTI Nifty Index Fund - Direct Plan - Growth Option", "code": "INF204KB14M2"},
                            {"name": "HDFC Index Fund-NIFTY 50 Plan - Direct Plan", "code": "INF179K01BB9"}
                        ]
                    }
                    
                    # Default to first category if not found
                    if fund_category not in fund_options:
                        fund_options[fund_category] = [{"name": "Sample Fund - Direct Plan - Growth Option", "code": "SAMPLE01"}]
                    
                    fund_list = fund_options.get(fund_category, [])
                    fund_names = [fund["name"] for fund in fund_list]
                    
                    selected_fund_name = st.selectbox("Select Fund", fund_names)
                    selected_fund = next((fund for fund in fund_list if fund["name"] == selected_fund_name), None)
                    
                    if selected_fund:
                        fund_code = selected_fund["code"]
                    else:
                        fund_code = "UNKNOWN"
                    
                    units = st.number_input("Number of Units", min_value=0.001, value=100.0, step=0.001)
                
                with col2:
                    st.markdown(
                        """
                        <div style="border-left: 4px solid #2196F3; padding-left: 10px;">
                        <p style="color: #2196F3; font-size: 1.2rem; margin-bottom: 5px;">Investment Details</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    
                    nav = st.number_input("Purchase NAV (₹)", min_value=0.01, value=50.0, step=0.01)
                    purchase_date = st.date_input("Purchase Date", value=datetime.now())
                    
                    # Show investment value
                    investment_value = units * nav
                    st.markdown(
                        f"""
                        <div style="background-color: rgba(33, 150, 243, 0.1); padding: 10px; border-radius: 5px; margin-top: 15px;">
                            <p style="font-weight: bold; margin-bottom: 5px;">Investment Summary</p>
                            <p>Total Investment: ₹{investment_value:,.2f}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # SIP option
                is_sip = st.checkbox("This is a Systematic Investment Plan (SIP)", 
                                  help="Check if this is a recurring investment in mutual funds")
                
                col_submit, _ = st.columns([1, 3])
                with col_submit:
                    submitted = st.form_submit_button("Add Mutual Fund", 
                                                   help="Add this mutual fund to your portfolio",
                                                   use_container_width=True)
                
                if submitted:
                    if selected_fund and units > 0 and nav > 0:
                        portfolio.add_mutual_fund(
                            fund_code,
                            units,
                            nav,
                            purchase_date.strftime('%Y-%m-%d'),
                            selected_fund_name
                        )
                        save_portfolio(portfolio)
                        st.success(f"✅ Successfully added {units} units of {selected_fund_name} to portfolio!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Please fill in all fields with valid values")
        
        with mf_redeem_tab:
            # Get mutual fund positions
            mutual_fund_positions = portfolio_value.get('mutual_fund_positions', [])
            
            if mutual_fund_positions:
                with st.form("redeem_mutual_fund_form", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(
                            """
                            <div style="border-left: 4px solid #FF9800; padding-left: 10px;">
                            <p style="color: #FF9800; font-size: 1.2rem; margin-bottom: 5px;">Fund Selection</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        # Create a list of funds in the portfolio
                        fund_codes = [mf['ticker'] for mf in mutual_fund_positions]
                        fund_names = [mf.get('fund_name', mf['ticker']) for mf in mutual_fund_positions]
                        
                        fund_display_options = {fund_names[i]: fund_codes[i] for i in range(len(fund_codes))}
                        
                        selected_fund_name = st.selectbox("Select Fund to Redeem", fund_names)
                        selected_fund_code = fund_display_options[selected_fund_name]
                        
                        # Find the position
                        selected_position = next((mf for mf in mutual_fund_positions if mf['ticker'] == selected_fund_code), None)
                        
                        if selected_position:
                            st.metric(
                                label="Current NAV", 
                                value=f"₹{selected_position['current_nav']:.2f}",
                                delta=f"{selected_position['gain_loss_pct']:.2f}%"
                            )
                            max_units = selected_position['units']
                            units_to_redeem = st.number_input("Number of Units to Redeem", 
                                                           min_value=0.001, 
                                                           max_value=float(max_units), 
                                                           value=float(max_units), 
                                                           step=0.001)
                    
                    with col2:
                        st.markdown(
                            """
                            <div style="border-left: 4px solid #9C27B0; padding-left: 10px;">
                            <p style="color: #9C27B0; font-size: 1.2rem; margin-bottom: 5px;">Redemption Details</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        current_nav = selected_position['current_nav'] if selected_position else 0
                        redemption_nav = st.number_input("Redemption NAV (₹)", 
                                                      min_value=0.01, 
                                                      value=float(current_nav), 
                                                      step=0.01)
                        redemption_date = st.date_input("Redemption Date", value=datetime.now())
                        
                        # Calculate and display potential profit/loss
                        if selected_position:
                            potential_pl = (redemption_nav - selected_position['avg_nav']) * units_to_redeem
                            pl_percent = (redemption_nav / selected_position['avg_nav'] - 1) * 100
                            pl_color = "green" if potential_pl >= 0 else "red"
                            pl_prefix = "+" if potential_pl >= 0 else ""
                            
                            st.markdown(
                                f"""
                                <div style="background-color: {'rgba(76, 175, 80, 0.1)' if potential_pl >= 0 else 'rgba(244, 67, 54, 0.1)'}; 
                                      padding: 10px; border-radius: 5px; margin-top: 15px;">
                                    <p style="font-weight: bold; margin-bottom: 5px;">Redemption Summary</p>
                                    <p>Potential Profit/Loss: <span style="color: {pl_color}; font-weight: bold;">
                                      {pl_prefix}₹{potential_pl:.2f} ({pl_prefix}{pl_percent:.2f}%)</span></p>
                                    <p>Total Redemption Value: ₹{redemption_nav * units_to_redeem:.2f}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    col_submit, _ = st.columns([1, 3])
                    with col_submit:
                        submitted = st.form_submit_button("Complete Redemption", 
                                                       help="Redeem units from your mutual fund portfolio",
                                                       use_container_width=True)
                    
                    if submitted:
                        if selected_fund_code and units_to_redeem > 0 and redemption_nav > 0:
                            success = portfolio.remove_mutual_fund(
                                selected_fund_code,
                                units_to_redeem,
                                redemption_nav,
                                redemption_date.strftime('%Y-%m-%d')
                            )
                            
                            if success:
                                save_portfolio(portfolio)
                                st.success(f"✅ Successfully redeemed {units_to_redeem} units of {selected_fund_name}!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to redeem mutual fund. Please try again.")
                        else:
                            st.error("❌ Please fill in all fields with valid values")
            else:
                st.info("No mutual funds in portfolio to redeem. Add mutual funds first.")
                st.button("Complete Redemption", disabled=True)
    
    # Portfolio Analysis
    if portfolio_value['positions']:
        st.subheader("Portfolio Analysis")
        
        # Get portfolio returns
        portfolio_returns = portfolio.get_portfolio_returns(period='1y')
        
        if portfolio_returns is not None and not portfolio_returns.empty:
            # Tabs for different analyses
            tab1, tab2, tab3, tab4 = st.tabs(["Performance", "Risk Analysis", "Allocation", "🔗 Share"])
            
            with tab1:
                # Performance metrics
                from utils.stock_data import get_market_indices
                indices = get_market_indices()
                sp500_data = indices.get('S&P 500')
                
                if sp500_data is not None:
                    # Calculate S&P 500 returns
                    sp500_returns = sp500_data['Close'].pct_change().dropna()
                    
                    # Align portfolio returns with S&P 500 returns
                    aligned_portfolio_returns = portfolio_returns['Portfolio_Daily_Return'].reindex(sp500_returns.index).dropna()
                    aligned_sp500_returns = sp500_returns.reindex(aligned_portfolio_returns.index)
                    
                    # Calculate performance metrics
                    performance_metrics = calculate_performance_metrics(
                        aligned_portfolio_returns, 
                        aligned_sp500_returns
                    )
                    
                    # Display performance metrics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        metrics_df1 = pd.DataFrame({
                            'Metric': ['Total Return', 'Annualized Return', 'Volatility', 'Sharpe Ratio'],
                            'Value': [
                                f"{performance_metrics['total_return']:.2f}%",
                                f"{performance_metrics['annualized_return']:.2f}%",
                                f"{performance_metrics['volatility']:.2f}%",
                                f"{performance_metrics['sharpe_ratio']:.2f}"
                            ]
                        })
                        st.table(metrics_df1)
                    
                    with col2:
                        metrics_df2 = pd.DataFrame({
                            'Metric': ['Sortino Ratio', 'Max Drawdown', 'Alpha', 'Beta'],
                            'Value': [
                                f"{performance_metrics['sortino_ratio']:.2f}",
                                f"{performance_metrics['max_drawdown']:.2f}%",
                                f"{performance_metrics['alpha']:.2f}%",
                                f"{performance_metrics['beta']:.2f}"
                            ]
                        })
                        st.table(metrics_df2)
                    
                    # Performance comparison chart
                    fig = go.Figure()
                    
                    # Portfolio returns
                    fig.add_trace(go.Scatter(
                        x=portfolio_returns.index,
                        y=portfolio_returns['Portfolio_Cumulative_Return'] * 100,
                        mode='lines',
                        name='Portfolio',
                        line=dict(color='#1E88E5', width=2)
                    ))
                    
                    # S&P 500 returns
                    sp500_cumulative_returns = (1 + sp500_returns).cumprod() - 1
                    fig.add_trace(go.Scatter(
                        x=sp500_cumulative_returns.index,
                        y=sp500_cumulative_returns * 100,
                        mode='lines',
                        name='S&P 500',
                        line=dict(color='#FFC107', width=1.5, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title='Performance Comparison',
                        xaxis_title='Date',
                        yaxis_title='Cumulative Return (%)',
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Unable to fetch benchmark data for comparison")
            
            with tab2:
                # Risk analysis
                if sp500_data is not None:
                    # Calculate risk metrics
                    risk_metrics = calculate_risk_metrics(aligned_portfolio_returns, aligned_sp500_returns)
                    
                    # Display risk metrics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        metrics_df1 = pd.DataFrame({
                            'Risk Metric': ['Daily VaR (95%)', 'Daily VaR (99%)', 'Monthly VaR (95%)'],
                            'Value': [
                                f"{risk_metrics['daily_var_95']:.2f}%",
                                f"{risk_metrics['daily_var_99']:.2f}%",
                                f"{risk_metrics['monthly_var_95']:.2f}%"
                            ]
                        })
                        st.table(metrics_df1)
                    
                    with col2:
                        metrics_df2 = pd.DataFrame({
                            'Risk Metric': ['Downside Deviation', 'Monthly Volatility', 'Correlation to Market'],
                            'Value': [
                                f"{risk_metrics['downside_deviation']:.2f}%",
                                f"{risk_metrics['monthly_volatility']:.2f}%",
                                f"{risk_metrics['correlation_to_market']:.2f}"
                            ]
                        })
                        st.table(metrics_df2)
                    
                    # Risk visualization - Value at Risk
                    fig = go.Figure()
                    
                    # Distribution of returns
                    fig.add_trace(go.Histogram(
                        x=aligned_portfolio_returns * 100,
                        nbinsx=30,
                        name='Return Distribution',
                        marker_color='#1E88E5'
                    ))
                    
                    # Add VaR lines
                    fig.add_vline(
                        x=-risk_metrics['daily_var_95'],
                        line_dash="dash",
                        line_color="red",
                        annotation_text="95% VaR",
                        annotation_position="top right"
                    )
                    
                    fig.add_vline(
                        x=-risk_metrics['daily_var_99'],
                        line_dash="dash",
                        line_color="darkred",
                        annotation_text="99% VaR",
                        annotation_position="top right"
                    )
                    
                    fig.update_layout(
                        title='Return Distribution and Value at Risk',
                        xaxis_title='Daily Return (%)',
                        yaxis_title='Frequency',
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Drawdown chart
                    cumulative_returns = (1 + aligned_portfolio_returns).cumprod() - 1
                    running_max = cumulative_returns.cummax()
                    drawdown = (cumulative_returns / running_max) - 1
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=drawdown.index,
                        y=drawdown * 100,
                        fill='tozeroy',
                        fillcolor='rgba(255, 0, 0, 0.2)',
                        line=dict(color='red', width=1),
                        name='Drawdown'
                    ))
                    
                    fig.update_layout(
                        title='Portfolio Drawdown',
                        xaxis_title='Date',
                        yaxis_title='Drawdown (%)',
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Unable to fetch data for risk analysis")
            
            with tab3:
                # Allocation analysis
                sector_allocation = calculate_sector_allocation(portfolio_value)
                
                if sector_allocation['sectors']:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Sector allocation pie chart
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
                            height=350,
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Sector allocation table
                        sectors_df = pd.DataFrame({
                            'Sector': sector_allocation['sectors'],
                            'Weight': [f"{w:.2f}%" for w in sector_allocation['weights']]
                        })
                        
                        st.table(sectors_df)
                    
                    # Asset allocation bar chart
                    asset_data = []
                    for pos in portfolio_value['positions']:
                        weight = (pos['current_value'] / portfolio_value['total_value']) * 100
                        asset_data.append({
                            'Ticker': pos['ticker'],
                            'Weight': weight
                        })
                    
                    asset_df = pd.DataFrame(asset_data)
                    asset_df = asset_df.sort_values('Weight', ascending=False)
                    
                    fig = px.bar(
                        asset_df,
                        x='Ticker',
                        y='Weight',
                        title='Asset Allocation',
                        text='Ticker'
                    )
                    
                    fig.update_traces(
                        textposition='inside',
                        marker_color='#1E88E5'
                    )
                    
                    fig.update_layout(
                        xaxis_title='',
                        yaxis_title='Weight (%)',
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Unable to analyze portfolio allocation")
                    
            with tab5:
                # Share portfolio functionality
                st.write("### Share Your Portfolio Insights")
                
                # Intro text with fancy styling
                st.markdown(
                    """
                    <div style="padding: 15px; border-radius: 5px; background: linear-gradient(to right, #e0f7fa, #b2ebf2); margin-bottom: 20px;">
                    <p style="margin:0; font-size: 1rem;">
                    Share your investment journey with friends and colleagues. 
                    Select what to share and use the buttons below to quickly generate shareable content for social media.
                    </p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Generate summary text based on portfolio performance
                if sp500_data is not None:
                    portfolio_summary_text = generate_text_summary(
                        portfolio_value, 
                        performance_metrics
                    )
                else:
                    portfolio_summary_text = generate_text_summary(
                        portfolio_value,
                        None
                    )
                
                # Share options in columns
                share_col1, share_col2 = st.columns([3, 2])
                
                with share_col1:
                    st.write("#### What would you like to share?")
                    share_options = st.multiselect(
                        "Select content to include",
                        options=["Portfolio Summary", "Performance Chart", "Allocation Chart", "Portfolio Card"],
                        default=["Portfolio Summary", "Portfolio Card"],
                        help="Choose what elements to include in your shared content"
                    )
                    
                    # Text preview
                    if "Portfolio Summary" in share_options:
                        st.text_area("Text Summary", portfolio_summary_text, height=150)
                    
                    # Get sharing links
                    share_links = get_share_links(portfolio_summary_text, title="My Investment Portfolio")
                    
                    st.write("#### Share via:")
                    
                    # Social sharing buttons with icons
                    share_btn_col1, share_btn_col2, share_btn_col3, share_btn_col4 = st.columns(4)
                    
                    with share_btn_col1:
                        twitter_btn = st.link_button(
                            "Twitter", 
                            share_links['twitter'],
                            help="Share on Twitter"
                        )
                    
                    with share_btn_col2:
                        whatsapp_btn = st.link_button(
                            "WhatsApp", 
                            share_links['whatsapp'],
                            help="Share on WhatsApp"
                        )
                    
                    with share_btn_col3:
                        telegram_btn = st.link_button(
                            "Telegram", 
                            share_links['telegram'],
                            help="Share on Telegram"
                        )
                    
                    with share_btn_col4:
                        email_btn = st.link_button(
                            "Email", 
                            share_links['email'],
                            help="Share via Email"
                        )
                    
                    # Copy text button
                    if st.button("📋 Copy Text to Clipboard", help="Copy the summary text to clipboard"):
                        st.code(portfolio_summary_text)
                        st.success("Text copied to clipboard! (You can manually copy from above)")
                
                with share_col2:
                    st.write("#### Preview")
                    
                    # Generate and preview different share formats
                    if "Portfolio Card" in share_options:
                        try:
                            performance_metrics_for_card = performance_metrics if sp500_data is not None else None
                            card_img_bytes = generate_shareable_portfolio_card(
                                portfolio_value, 
                                performance_metrics_for_card
                            )
                            st.image(card_img_bytes, caption="Portfolio Summary Card", use_column_width=True)
                            st.markdown(get_image_download_link(card_img_bytes, "portfolio_card.png", "📥 Download Card"), unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Could not generate portfolio card: {e}")
                    
                    # QR code for quick sharing
                    try:
                        qr_bytes = generate_qr_code(portfolio_summary_text)
                        st.image(qr_bytes, caption="Scan to Share", width=150)
                        st.markdown(get_image_download_link(qr_bytes, "portfolio_qr.png", "📥 Download QR Code"), unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Could not generate QR code: {e}")
                
                # Visual charts for sharing
                if "Performance Chart" in share_options or "Allocation Chart" in share_options:
                    st.write("#### Visual Content to Share")
                    
                    viz_col1, viz_col2 = st.columns(2)
                    
                    if "Performance Chart" in share_options and sp500_data is not None:
                        with viz_col1:
                            try:
                                perf_img_bytes = generate_performance_image(
                                    portfolio_returns, 
                                    sp500_returns
                                )
                                st.image(perf_img_bytes, caption="Performance Chart", use_column_width=True)
                                st.markdown(get_image_download_link(perf_img_bytes, "performance_chart.png", "📥 Download Chart"), unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Could not generate performance chart: {e}")
                    
                    if "Allocation Chart" in share_options:
                        with viz_col2:
                            try:
                                alloc_img_bytes = generate_allocation_image(portfolio_value)
                                st.image(alloc_img_bytes, caption="Allocation Chart", use_column_width=True)
                                st.markdown(get_image_download_link(alloc_img_bytes, "allocation_chart.png", "📥 Download Chart"), unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Could not generate allocation chart: {e}")
                
                # AI-generated investment insights
                st.write("#### AI-Generated Investment Insight")
                
                # Generate a simple insight about the portfolio
                insight_placeholder = st.empty()
                
                if st.button("Generate Shareable Insight"):
                    with st.spinner("Analyzing your portfolio..."):
                        # Simulate AI processing
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        # Portfolio metrics analysis
                        if sp500_data is not None and performance_metrics:
                            total_return = performance_metrics.get('total_return', 0)
                            sharpe = performance_metrics.get('sharpe_ratio', 0)
                            beta = performance_metrics.get('beta', 0)
                            
                            # Generate insight based on metrics
                            if sharpe > 1:
                                risk_comment = "Your portfolio shows a good risk-adjusted return."
                            elif sharpe > 0.5:
                                risk_comment = "Your portfolio has moderate risk-adjusted returns."
                            else:
                                risk_comment = "Consider adjusting your portfolio for better risk-adjusted returns."
                            
                            if beta < 0.8:
                                beta_comment = "Your portfolio is less volatile than the market."
                            elif beta < 1.2:
                                beta_comment = "Your portfolio moves closely with the market."
                            else:
                                beta_comment = "Your portfolio is more volatile than the market."
                            
                            insight = f"""
                            📊 **Portfolio Insight**: Your portfolio has returned {total_return:.2f}% and has a Sharpe ratio of {sharpe:.2f}. {risk_comment} 
                            
                            💡 **Market Correlation**: With a beta of {beta:.2f}, {beta_comment} 
                            
                            🔍 **Recommendation**: {'Consider adding more defensive stocks for stability.' if beta > 1.2 else 'Your current asset allocation appears balanced. Consider reviewing quarterly.'}
                            """
                        else:
                            insight = """
                            📊 **Portfolio Insight**: Based on your current allocation, your portfolio is diversified across multiple assets.
                            
                            💡 **Suggestion**: Consider setting up a regular review schedule to rebalance your portfolio quarterly.
                            
                            🔍 **Next Steps**: Track your portfolio performance against key market indices to gauge relative performance.
                            """
                        
                        # Display the insight
                        insight_placeholder.markdown(insight)
                        
                        # Add share this insight button
                        st.button("Share this Insight", help="Share this AI-generated insight with your network")
        else:
            st.warning("Not enough data to analyze portfolio")
