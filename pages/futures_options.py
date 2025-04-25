import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from utils.stock_data import (
    get_stock_data, 
    get_futures_options_data,
    forecast_futures_indices
)
from utils.currency import format_currency, convert_usd_to_inr

def show():
    """Display the futures and options analysis page"""
    st.title("Futures & Options Analysis")
    
    # Add page description
    st.markdown(
        """
        Analyze futures and options data for Indian markets. This page provides:
        - Futures indices forecasting for NIFTY and SENSEX
        - Options chain analysis 
        - Option pricing visualization
        """
    )
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["Futures Forecasting", "Options Analysis"])
    
    with tab1:
        show_futures_forecasting()
    
    with tab2:
        show_options_analysis()

def show_futures_forecasting():
    """Display the futures forecasting section"""
    st.subheader("Futures Forecasting")
    
    # Select an index to forecast
    indices = {
        'NIFTY 50': '^NSEI',
        'SENSEX': '^BSESN',
        'NIFTY Bank': '^NSEBANK'
    }
    
    selected_index = st.selectbox(
        "Select Index for Forecasting",
        list(indices.keys())
    )
    
    ticker = indices[selected_index]
    
    # Days to forecast
    days_forward = st.slider(
        "Days to Forecast",
        min_value=1,
        max_value=10,
        value=5
    )
    
    # Generate forecast
    with st.spinner(f"Forecasting {selected_index} futures..."):
        forecast_data = forecast_futures_indices(ticker, days_forward)
    
    if forecast_data is None:
        st.error("Could not generate forecast. Please try another index.")
        return
    
    # Display forecast results
    st.markdown(f"### Forecast Results for {selected_index}")
    
    # Current value
    st.metric(
        "Current Value",
        f"₹{forecast_data['last_price']:,.2f}",
        delta=None
    )
    
    # Show forecast table
    if forecast_data['forecast']:
        forecast_df = pd.DataFrame(forecast_data['forecast'])
        
        # Format values with Rupee symbol
        forecast_df['prediction'] = forecast_df['prediction'].map(lambda x: f"₹{x:,.2f}")
        forecast_df['lower_bound'] = forecast_df['lower_bound'].map(lambda x: f"₹{x:,.2f}")
        forecast_df['upper_bound'] = forecast_df['upper_bound'].map(lambda x: f"₹{x:,.2f}")
        
        # Rename columns for display
        forecast_df.columns = ['Date', 'Prediction', 'Lower Bound', 'Upper Bound']
        
        st.table(forecast_df)
        
        # Create visualization of forecast
        raw_forecast = pd.DataFrame(forecast_data['forecast'])
        
        # Historical data for context
        historical = get_stock_data(ticker, period='30d')
        
        if historical is not None and not historical.empty:
            # Create the graph
            fig = go.Figure()
            
            # Add historical data
            fig.add_trace(go.Scatter(
                x=historical.index,
                y=historical['Close'],
                mode='lines',
                name='Historical',
                line=dict(color='blue', width=2)
            ))
            
            # Add forecast
            dates = pd.to_datetime(raw_forecast['date'])
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=raw_forecast['prediction'],
                mode='lines+markers',
                name='Forecast',
                line=dict(color='green', width=2)
            ))
            
            # Add confidence intervals
            fig.add_trace(go.Scatter(
                x=dates.tolist() + dates.tolist()[::-1],
                y=raw_forecast['upper_bound'].tolist() + raw_forecast['lower_bound'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(0,176,0,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval'
            ))
            
            fig.update_layout(
                title=f"{selected_index} Forecast",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=500,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        # Forecast insights
        st.subheader("Forecast Insights")
        
        # Calculate expected change
        last_day_prediction = float(raw_forecast['prediction'].iloc[-1])
        expected_change = ((last_day_prediction / forecast_data['last_price']) - 1) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                f"Expected in {days_forward} days",
                f"₹{last_day_prediction:,.2f}",
                f"{expected_change:+.2f}%",
                delta_color="normal"
            )
        
        with col2:
            volatility_annual = forecast_data['daily_volatility'] * (252 ** 0.5) * 100
            st.metric(
                "Annualized Volatility",
                f"{volatility_annual:.2f}%",
                None
            )
            
        with col3:
            # Risk assessment based on volatility
            risk_level = "High" if volatility_annual > 25 else "Medium" if volatility_annual > 15 else "Low"
            risk_color = {"High": "red", "Medium": "orange", "Low": "green"}
            st.markdown(
                f"""
                <div style='border:1px solid {risk_color[risk_level]}; border-radius:5px; padding:10px;'>
                <h3 style='color:{risk_color[risk_level]};'>Risk Level: {risk_level}</h3>
                <p>Based on historical volatility</p>
                </div>
                """,
                unsafe_allow_html=True
            )

def show_options_analysis():
    """Display the options analysis section"""
    st.subheader("Options Analysis")
    
    # Select a stock or index to analyze
    option_stocks = {
        'NIFTY 50': '^NSEI',
        'SENSEX': '^BSESN',
        'Reliance Industries': 'RELIANCE.NS',
        'HDFC Bank': 'HDFCBANK.NS',
        'Infosys': 'INFY.NS',
        'TCS': 'TCS.NS',
        'ICICI Bank': 'ICICIBANK.NS',
        'Bajaj Finance': 'BAJFINANCE.NS'
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_stock = st.selectbox(
            "Select Stock/Index for Options Analysis",
            list(option_stocks.keys())
        )
    
    ticker = option_stocks[selected_stock]
    
    # Get options data
    with st.spinner(f"Loading options data for {selected_stock}..."):
        options_data = get_futures_options_data(ticker)
    
    if options_data is None:
        st.error("No options data available for this instrument. Try another selection.")
        return
    
    # Expiration date selection
    with col2:
        if 'all_expirations' in options_data and options_data['all_expirations']:
            selected_expiration = st.selectbox(
                "Expiration Date",
                options_data['all_expirations'],
                index=0
            )
            # Reload data with the selected expiration if it changed
            if selected_expiration != options_data['expiration_date']:
                with st.spinner(f"Loading options data for {selected_stock} with expiration {selected_expiration}..."):
                    options_data = get_futures_options_data(ticker, selected_expiration)
    
    # Display options information
    if 'current_price' in options_data and options_data['current_price']:
        st.markdown(f"### Options Chain for {selected_stock} - Current Price: ₹{options_data['current_price']:,.2f}")
    else:
        st.markdown(f"### Options Chain for {selected_stock}")
    
    st.markdown(f"**Expiration Date:** {options_data['expiration_date']}")
    
    # Create tabs for calls and puts, and option analytics
    call_tab, put_tab, analysis_tab = st.tabs(["Call Options", "Put Options", "Options Analytics"])
    
    with call_tab:
        calls_df = options_data['calls']
        
        if calls_df is not None and not calls_df.empty:
            # Add toggle for additional columns like Greeks
            show_advanced = st.checkbox("Show Advanced Metrics (Greeks)", key="calls_advanced")
            
            # Clean up the dataframe
            base_cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']
            
            if show_advanced and 'status' in calls_df.columns:
                display_cols = base_cols + ['status', 'theta']
            else:
                display_cols = base_cols
                
            if all(col in calls_df.columns for col in base_cols):
                display_df = calls_df[display_cols].copy()
                
                # Rename columns for better readability
                col_mapping = {
                    'strike': 'Strike Price', 
                    'lastPrice': 'Last Price', 
                    'bid': 'Bid', 
                    'ask': 'Ask', 
                    'volume': 'Volume', 
                    'openInterest': 'Open Interest', 
                    'impliedVolatility': 'Implied Volatility',
                    'status': 'Status',
                    'theta': 'Theta (₹/day)'
                }
                
                display_df.columns = [col_mapping.get(col, col) for col in display_cols]
                
                # Convert to INR for display
                for col in ['Strike Price', 'Last Price', 'Bid', 'Ask']:
                    display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else "N/A")
                
                # Format volatility as percentage
                display_df['Implied Volatility'] = display_df['Implied Volatility'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
                
                if 'Theta (₹/day)' in display_df.columns:
                    display_df['Theta (₹/day)'] = display_df['Theta (₹/day)'].apply(lambda x: f"₹{x:.2f}" if pd.notna(x) else "N/A")
                
                # Add color highlighting based on moneyness
                if 'Status' in display_df.columns:
                    def highlight_status(row):
                        if row['Status'] == 'ITM':
                            return ['background-color: rgba(0,200,83,0.2)'] * len(row)
                        elif row['Status'] == 'OTM':
                            return ['background-color: rgba(255,82,82,0.1)'] * len(row)
                        else:  # ATM
                            return ['background-color: rgba(255,215,0,0.2)'] * len(row)
                    
                    st.dataframe(
                        display_df.style.apply(highlight_status, axis=1) if 'Status' in display_df.columns else display_df,
                        use_container_width=True
                    )
                else:
                    st.dataframe(display_df, use_container_width=True)
                
                # Visualizations
                st.subheader("Call Options Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Visualization of open interest
                    if 'openInterest' in calls_df.columns and 'strike' in calls_df.columns:
                        fig = px.bar(
                            calls_df,
                            x='strike',
                            y='openInterest',
                            title='Call Options Open Interest by Strike Price',
                            labels={'strike': 'Strike Price (₹)', 'openInterest': 'Open Interest'},
                            color_discrete_sequence=['#00C853']
                        )
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Implied volatility smile/skew
                    if 'impliedVolatility' in calls_df.columns and 'strike' in calls_df.columns:
                        # Filter out extreme values
                        volatility_df = calls_df[calls_df['impliedVolatility'] < 2]  # Filter out >200% volatility
                        
                        if not volatility_df.empty:
                            fig = px.line(
                                volatility_df,
                                x='strike',
                                y='impliedVolatility',
                                title='Call Options Implied Volatility Curve',
                                labels={'strike': 'Strike Price (₹)', 'impliedVolatility': 'Implied Volatility'},
                                markers=True
                            )
                            
                            # Add current price reference line if available
                            if 'current_price' in options_data and options_data['current_price']:
                                fig.add_vline(
                                    x=options_data['current_price'], 
                                    line_dash="dash", 
                                    line_color="orange",
                                    annotation_text="Current Price",
                                    annotation_position="top right"
                                )
                            
                            fig.update_layout(height=350)
                            fig.update_yaxes(tickformat='.0%')
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Limited options data available - missing some expected columns.")
                st.dataframe(calls_df)
        else:
            st.info("No call options data available.")
    
    with put_tab:
        puts_df = options_data['puts']
        
        if puts_df is not None and not puts_df.empty:
            # Add toggle for additional columns like Greeks
            show_advanced = st.checkbox("Show Advanced Metrics (Greeks)", key="puts_advanced")
            
            # Clean up the dataframe
            base_cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']
            
            if show_advanced and 'status' in puts_df.columns:
                display_cols = base_cols + ['status', 'theta']
            else:
                display_cols = base_cols
                
            if all(col in puts_df.columns for col in base_cols):
                display_df = puts_df[display_cols].copy()
                
                # Rename columns for better readability
                col_mapping = {
                    'strike': 'Strike Price', 
                    'lastPrice': 'Last Price', 
                    'bid': 'Bid', 
                    'ask': 'Ask', 
                    'volume': 'Volume', 
                    'openInterest': 'Open Interest', 
                    'impliedVolatility': 'Implied Volatility',
                    'status': 'Status',
                    'theta': 'Theta (₹/day)'
                }
                
                display_df.columns = [col_mapping.get(col, col) for col in display_cols]
                
                # Convert to INR for display
                for col in ['Strike Price', 'Last Price', 'Bid', 'Ask']:
                    display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else "N/A")
                
                # Format volatility as percentage
                display_df['Implied Volatility'] = display_df['Implied Volatility'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
                
                if 'Theta (₹/day)' in display_df.columns:
                    display_df['Theta (₹/day)'] = display_df['Theta (₹/day)'].apply(lambda x: f"₹{x:.2f}" if pd.notna(x) else "N/A")
                
                # Add color highlighting based on moneyness
                if 'Status' in display_df.columns:
                    def highlight_status(row):
                        if row['Status'] == 'ITM':
                            return ['background-color: rgba(0,200,83,0.2)'] * len(row)
                        elif row['Status'] == 'OTM':
                            return ['background-color: rgba(255,82,82,0.1)'] * len(row)
                        else:  # ATM
                            return ['background-color: rgba(255,215,0,0.2)'] * len(row)
                    
                    st.dataframe(
                        display_df.style.apply(highlight_status, axis=1) if 'Status' in display_df.columns else display_df,
                        use_container_width=True
                    )
                else:
                    st.dataframe(display_df, use_container_width=True)
                
                # Visualizations
                st.subheader("Put Options Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Visualization of open interest
                    if 'openInterest' in puts_df.columns and 'strike' in puts_df.columns:
                        fig = px.bar(
                            puts_df,
                            x='strike',
                            y='openInterest',
                            title='Put Options Open Interest by Strike Price',
                            labels={'strike': 'Strike Price (₹)', 'openInterest': 'Open Interest'},
                            color_discrete_sequence=['#FF5252']
                        )
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Implied volatility smile/skew
                    if 'impliedVolatility' in puts_df.columns and 'strike' in puts_df.columns:
                        # Filter out extreme values
                        volatility_df = puts_df[puts_df['impliedVolatility'] < 2]  # Filter out >200% volatility
                        
                        if not volatility_df.empty:
                            fig = px.line(
                                volatility_df,
                                x='strike',
                                y='impliedVolatility',
                                title='Put Options Implied Volatility Curve',
                                labels={'strike': 'Strike Price (₹)', 'impliedVolatility': 'Implied Volatility'},
                                markers=True
                            )
                            
                            # Add current price reference line if available
                            if 'current_price' in options_data and options_data['current_price']:
                                fig.add_vline(
                                    x=options_data['current_price'], 
                                    line_dash="dash", 
                                    line_color="orange",
                                    annotation_text="Current Price",
                                    annotation_position="top right"
                                )
                            
                            fig.update_layout(height=350)
                            fig.update_yaxes(tickformat='.0%')
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Limited options data available - missing some expected columns.")
                st.dataframe(puts_df)
        else:
            st.info("No put options data available.")
            
    with analysis_tab:
        st.subheader("Options Analysis Tools")
        
        if 'current_price' in options_data and options_data['current_price']:
            current_price = options_data['current_price']
            
            # Max Pain Analysis (the strike price at which option writers have the least amount of financial loss)
            if 'calls' in options_data and 'puts' in options_data and 'strike' in calls_df.columns and 'openInterest' in calls_df.columns:
                st.markdown("### Max Pain Analysis")
                st.markdown("""
                **Max Pain Theory**: The point where option writers (sellers) will lose the least amount of money.
                The theory suggests that the underlying price will gravitate towards this point on expiration.
                """)
                
                # Calculate max pain
                strikes = sorted(set(calls_df['strike'].tolist()).union(set(puts_df['strike'].tolist())))
                
                pain_values = []
                for strike in strikes:
                    # Calculate pain for call options at this strike
                    call_pain = sum(max(0, current_price - k) * oi for k, oi in 
                                  zip(calls_df['strike'], calls_df['openInterest']) if k <= strike)
                    
                    # Calculate pain for put options at this strike
                    put_pain = sum(max(0, k - current_price) * oi for k, oi in 
                                 zip(puts_df['strike'], puts_df['openInterest']) if k >= strike)
                    
                    total_pain = call_pain + put_pain
                    pain_values.append((strike, total_pain))
                
                # Find the strike with minimum pain
                max_pain_strike = min(pain_values, key=lambda x: x[1])[0]
                
                # Display max pain
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Max Pain Point",
                        f"₹{max_pain_strike:,.2f}",
                        f"{((max_pain_strike / current_price) - 1) * 100:.2f}% from current price"
                    )
                
                with col2:
                    # Create DataFrame for plotting
                    pain_df = pd.DataFrame(pain_values, columns=['Strike', 'Pain'])
                    
                    fig = px.line(
                        pain_df, 
                        x='Strike', 
                        y='Pain',
                        title='Option Pain by Strike Price',
                        labels={'Strike': 'Strike Price (₹)', 'Pain': 'Total Pain Value'},
                        markers=True
                    )
                    
                    # Add vertical lines for max pain and current price
                    fig.add_vline(
                        x=max_pain_strike, 
                        line_dash="solid", 
                        line_color="green",
                        annotation_text="Max Pain",
                        annotation_position="top right"
                    )
                    
                    fig.add_vline(
                        x=current_price, 
                        line_dash="dash", 
                        line_color="blue",
                        annotation_text="Current Price",
                        annotation_position="top left"
                    )
                    
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Put/Call Ratio Analysis
            st.markdown("### Put/Call Ratio Analysis")
            st.markdown("""
            **Put/Call Ratio**: A sentiment indicator that shows the relationship between put and call volume.
            - High ratio (>1): More puts than calls, suggesting bearish sentiment
            - Low ratio (<1): More calls than puts, suggesting bullish sentiment
            """)
            
            if not calls_df.empty and not puts_df.empty:
                total_call_volume = calls_df['volume'].sum() if 'volume' in calls_df.columns else 0
                total_put_volume = puts_df['volume'].sum() if 'volume' in puts_df.columns else 0
                
                total_call_oi = calls_df['openInterest'].sum() if 'openInterest' in calls_df.columns else 0
                total_put_oi = puts_df['openInterest'].sum() if 'openInterest' in puts_df.columns else 0
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Volume-based P/C ratio
                    if total_call_volume > 0:
                        volume_pc_ratio = total_put_volume / total_call_volume
                        
                        # Determine sentiment based on ratio
                        if volume_pc_ratio > 1.2:
                            sentiment = "Bearish"
                            color = "red"
                        elif volume_pc_ratio < 0.8:
                            sentiment = "Bullish"
                            color = "green"
                        else:
                            sentiment = "Neutral"
                            color = "orange"
                        
                        st.markdown(f"""
                        <div style="border: 1px solid {color}; border-radius: 5px; padding: 10px; text-align: center;">
                            <h3>Volume Put/Call Ratio</h3>
                            <p style="font-size: 24px; color: {color};">{volume_pc_ratio:.2f}</p>
                            <p>Market Sentiment: <strong style="color: {color};">{sentiment}</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Insufficient volume data to calculate Put/Call ratio")
                
                with col2:
                    # Open Interest-based P/C ratio
                    if total_call_oi > 0:
                        oi_pc_ratio = total_put_oi / total_call_oi
                        
                        # Determine sentiment based on ratio
                        if oi_pc_ratio > 1.2:
                            sentiment = "Bearish"
                            color = "red"
                        elif oi_pc_ratio < 0.8:
                            sentiment = "Bullish"
                            color = "green"
                        else:
                            sentiment = "Neutral"
                            color = "orange"
                        
                        st.markdown(f"""
                        <div style="border: 1px solid {color}; border-radius: 5px; padding: 10px; text-align: center;">
                            <h3>Open Interest Put/Call Ratio</h3>
                            <p style="font-size: 24px; color: {color};">{oi_pc_ratio:.2f}</p>
                            <p>Market Sentiment: <strong style="color: {color};">{sentiment}</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Insufficient open interest data to calculate Put/Call ratio")
        else:
            st.info("Current price information is not available for detailed analysis")
            
    
    # Display option strategies
    st.markdown("### Common Option Strategies")
    
    strategy = st.selectbox(
        "Select a strategy to learn more",
        [
            "Select a strategy",
            "Covered Call",
            "Protective Put",
            "Bull Call Spread",
            "Bear Put Spread",
            "Straddle",
            "Strangle"
        ]
    )
    
    if strategy != "Select a strategy":
        # Display strategy information
        strategy_info = {
            "Covered Call": {
                "description": "A strategy where you own the underlying stock and sell a call option against it.",
                "use_case": "When you expect the stock to remain flat or rise slightly.",
                "risk": "Limited upside potential, but reduced cost basis.",
                "example": "Buy 100 shares of Reliance and sell 1 OTM call option."
            },
            "Protective Put": {
                "description": "A strategy where you own the underlying stock and buy a put option to protect against downside.",
                "use_case": "When you want to protect against a significant downside move.",
                "risk": "Cost of the put option (premium).",
                "example": "Buy 100 shares of HDFC Bank and buy 1 put option at or near the current price."
            },
            "Bull Call Spread": {
                "description": "Buy a call option and sell a higher strike call option with the same expiration.",
                "use_case": "When you expect a moderate rise in the stock or index.",
                "risk": "Limited to the net premium paid.",
                "example": "Buy NIFTY 22000 call and sell NIFTY 22500 call."
            },
            "Bear Put Spread": {
                "description": "Buy a put option and sell a lower strike put option with the same expiration.",
                "use_case": "When you expect a moderate decline in the stock or index.",
                "risk": "Limited to the net premium paid.",
                "example": "Buy NIFTY 22000 put and sell NIFTY 21500 put."
            },
            "Straddle": {
                "description": "Buy a call and a put at the same strike price and expiration.",
                "use_case": "When you expect a large move but are uncertain of the direction.",
                "risk": "Limited to the combined premium paid for both options.",
                "example": "Buy both a NIFTY 22000 call and a NIFTY 22000 put."
            },
            "Strangle": {
                "description": "Buy a call with a higher strike price and a put with a lower strike price, same expiration.",
                "use_case": "When you expect a large move but are uncertain of the direction, and want to reduce cost.",
                "risk": "Limited to the combined premium paid for both options.",
                "example": "Buy a NIFTY 22500 call and a NIFTY 21500 put."
            }
        }
        
        info = strategy_info[strategy]
        
        st.markdown(f"""
        ### {strategy}
        
        **Description:** {info['description']}
        
        **Use Case:** {info['use_case']}
        
        **Risk Profile:** {info['risk']}
        
        **Example:** {info['example']}
        """)
        
        # Simple visual representation of the strategy's payoff
        st.markdown("#### Visual Payoff at Expiration")
        
        # Generate a simple payoff graph based on the strategy
        x = list(range(90, 111))  # Range from -10% to +10% of base price
        fig = None
        
        if strategy == "Covered Call":
            # Covered call payoff
            y = [min(10, val - 90) for val in x]
            fig = px.line(
                x=x, 
                y=y, 
                labels={"x": "Stock Price (%)", "y": "Profit/Loss"},
                title="Covered Call Payoff Diagram"
            )
            
        elif strategy == "Protective Put":
            # Protective put payoff
            y = [max(val - 100, 0) - 2 for val in x]
            fig = px.line(
                x=x, 
                y=y, 
                labels={"x": "Stock Price (%)", "y": "Profit/Loss"},
                title="Protective Put Payoff Diagram"
            )
            
        elif strategy == "Bull Call Spread":
            # Bull call spread payoff
            y = [max(min(val - 95, 5), -2) for val in x]
            fig = px.line(
                x=x, 
                y=y, 
                labels={"x": "Stock Price (%)", "y": "Profit/Loss"},
                title="Bull Call Spread Payoff Diagram"
            )
            
        elif strategy == "Bear Put Spread":
            # Bear put spread payoff
            y = [max(min(105 - val, 5), -2) for val in x]
            fig = px.line(
                x=x, 
                y=y, 
                labels={"x": "Stock Price (%)", "y": "Profit/Loss"},
                title="Bear Put Spread Payoff Diagram"
            )
            
        elif strategy == "Straddle":
            # Straddle payoff
            y = [max(abs(val - 100) - 5, -5) for val in x]
            fig = px.line(
                x=x, 
                y=y, 
                labels={"x": "Stock Price (%)", "y": "Profit/Loss"},
                title="Straddle Payoff Diagram"
            )
            
        elif strategy == "Strangle":
            # Strangle payoff
            y = [max(max(val - 105, 95 - val), -3) for val in x]
            fig = px.line(
                x=x, 
                y=y, 
                labels={"x": "Stock Price (%)", "y": "Profit/Loss"},
                title="Strangle Payoff Diagram"
            )
        
        # Display the payoff diagram if we have a figure
        if fig is not None:
            # Add reference line at y=0
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            # Add reference line at x=100 (current price)
            fig.add_vline(x=100, line_dash="dash", line_color="gray")
            
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis=dict(tickmode='linear', tick0=90, dtick=5),
                yaxis=dict(tickmode='linear', tick0=-10, dtick=5)
            )
            
            st.plotly_chart(fig, use_container_width=True)