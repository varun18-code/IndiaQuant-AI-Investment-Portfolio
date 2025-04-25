import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.stock_data import get_stock_data, get_stock_info
from utils.alternative_data import (
    simulate_satellite_imagery_data,
    simulate_shipping_data,
    generate_credit_card_spending_data,
    generate_weather_impact_data,
    generate_agricultural_satellite_data,
    generate_social_media_trends,
    generate_mobile_location_data,
    get_alternative_data
)

def show():
    """Display the alternative data page"""
    st.header("Alternative Data Analysis")
    
    # Default ticker
    default_ticker = "AAPL"
    
    # Select stock
    ticker = st.text_input("Enter Ticker Symbol", value=default_ticker).upper()
    
    # Fetch stock info
    stock_info = get_stock_info(ticker)
    
    if stock_info and stock_info.get('shortName') != 'N/A':
        # Stock name and basic info
        st.subheader(f"{stock_info['shortName']} ({ticker}) Alternative Data Analysis")
        
        # Create tabs for different alternative data analyses
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Retail/Foot Traffic", "Shipping & Supply Chain", "Consumer Spending", 
                                   "Agricultural Satellite", "Weather Impact", "Social Media Trends"])
        
        with tab1:
            # Retail/Foot Traffic Analysis
            st.subheader("Retail/Manufacturing Activity")
            
            # Time period selection
            activity_period = st.selectbox(
                "Analysis Timeframe",
                ["30 days", "60 days", "90 days"],
                index=0
            )
            
            # Convert period to number of days
            days = int(activity_period.split()[0])
            
            # Fetch satellite data
            satellite_data = simulate_satellite_imagery_data(ticker, days=days)
            
            if satellite_data:
                # Display activity overview
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Current activity metric
                    metric_name = satellite_data['metric_name']
                    current_value = satellite_data['current_value']
                    weekly_change = satellite_data['weekly_change_pct']
                    
                    # Color based on sentiment
                    color = {
                        'positive': 'green',
                        'negative': 'red',
                        'neutral': 'gray'
                    }[satellite_data['sentiment']]
                    
                    st.markdown(
                        f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px;'>"
                        f"<h3>{metric_name}</h3>"
                        f"<p style='font-size:2em; margin:5px 0;'>{current_value:.1f}</p>"
                        f"<p>Weekly change: <span style='color:{color}'>{'↑' if weekly_change > 0 else '↓'} {abs(weekly_change):.1f}%</span></p>"
                        f"<p>Business Type: {satellite_data['business_type'].capitalize()}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Insight card
                    st.markdown(
                        f"<div style='background-color:rgba({{'green': '76, 175, 80', 'red': '244, 67, 54', 'gray': '158, 158, 158'}}['{color}'], 0.1); padding:10px; border-left:3px solid {{'green': '#4CAF50', 'red': '#F44336', 'gray': '#9E9E9E'}}['{color}']; margin-top:10px;'>"
                        f"<h4 style='margin:0;'>Key Insight</h4>"
                        f"<p>{satellite_data['insight']}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                
                with col2:
                    # Activity trend chart
                    fig = go.Figure()
                    
                    # Add activity line
                    fig.add_trace(go.Scatter(
                        x=satellite_data['dates'],
                        y=satellite_data['activity'],
                        mode='lines+markers',
                        name=metric_name,
                        line=dict(color='#1E88E5', width=2),
                        marker=dict(size=5)
                    ))
                    
                    # Add trend line (7-day moving average)
                    ma_window = min(7, len(satellite_data['activity']))
                    activity_ma = pd.Series(satellite_data['activity']).rolling(window=ma_window).mean()
                    
                    fig.add_trace(go.Scatter(
                        x=satellite_data['dates'],
                        y=activity_ma,
                        mode='lines',
                        name='7-day Trend',
                        line=dict(color='#FF9800', width=1.5, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f'{metric_name} Trend',
                        xaxis_title='Date',
                        yaxis_title=metric_name,
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Activity vs. Stock Price
                st.subheader(f"{metric_name} vs. Stock Price")
                
                # Fetch stock price data
                price_period = "3mo" if days > 60 else "1mo"
                stock_data = get_stock_data(ticker, period=price_period)
                
                if stock_data is not None and not stock_data.empty:
                    # Create a figure with dual axes
                    fig = go.Figure()
                    
                    # Add stock price
                    fig.add_trace(go.Scatter(
                        x=stock_data.index,
                        y=stock_data['Close'],
                        mode='lines',
                        name='Stock Price',
                        line=dict(color='#1E88E5', width=2),
                        yaxis='y'
                    ))
                    
                    # Convert satellite data dates to datetime
                    sat_dates = [datetime.strptime(d, '%Y-%m-%d') for d in satellite_data['dates']]
                    
                    # Add activity data
                    fig.add_trace(go.Scatter(
                        x=sat_dates,
                        y=satellite_data['activity'],
                        mode='lines',
                        name=metric_name,
                        line=dict(color='#4CAF50', width=1.5),
                        yaxis='y2'
                    ))
                    
                    fig.update_layout(
                        title=f'{ticker} Price vs. {metric_name}',
                        xaxis_title='Date',
                        yaxis_title='Price (₹)',
                        yaxis2=dict(
                            title=metric_name,
                            titlefont=dict(color='rgba(76, 175, 80, 0.8)'),
                            tickfont=dict(color='rgba(76, 175, 80, 0.8)'),
                            overlaying='y',
                            side='right',
                            showgrid=False
                        ),
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate correlation if we have enough data
                    if len(satellite_data['activity']) > 5 and len(stock_data) > 5:
                        # Sample down to aligned dates
                        activity_df = pd.DataFrame({
                            'Date': sat_dates,
                            'Activity': satellite_data['activity']
                        })
                        
                        price_df = pd.DataFrame({
                            'Date': stock_data.index,
                            'Price': stock_data['Close']
                        })
                        
                        # Merge based on nearest dates
                        merged_df = pd.merge_asof(
                            activity_df.sort_values('Date'),
                            price_df.sort_values('Date'),
                            on='Date',
                            direction='nearest'
                        )
                        
                        if len(merged_df) > 5:
                            correlation = merged_df['Activity'].corr(merged_df['Price'])
                            
                            # Display correlation
                            st.markdown(
                                f"<div style='text-align:center; padding:10px; background-color:rgba(0,0,0,0.05); border-radius:5px;'>"
                                f"<h4>Correlation between {metric_name} and Stock Price</h4>"
                                f"<p style='font-size:1.5em; margin:5px 0;'>{correlation:.2f}</p>"
                                f"<p>{interpret_correlation(correlation)}</p>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                else:
                    st.warning(f"Unable to fetch price data for {ticker}")
                
                # About the data
                st.markdown("""
                **About this data:** This analysis is based on simulated satellite imagery data that tracks 
                retail foot traffic or manufacturing activity. In a real-world scenario, this data would be 
                derived from actual satellite imagery and computer vision algorithms that count cars in parking 
                lots, measure factory activity, or track other physical indicators of business performance.
                """)
            else:
                st.warning(f"No satellite imagery data available for {ticker}")
        
        with tab2:
            # Shipping & Supply Chain Analysis
            st.subheader("Global Shipping & Supply Chain")
            
            # Time period selection
            shipping_period = st.selectbox(
                "Analysis Timeframe",
                ["30 days", "60 days", "90 days"],
                index=0,
                key="shipping_period"
            )
            
            # Convert period to number of days
            shipping_days = int(shipping_period.split()[0])
            
            # Fetch shipping data
            shipping_data = simulate_shipping_data(days=shipping_days)
            
            if shipping_data:
                # Display shipping overview
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Current congestion metric
                    current_congestion = shipping_data['current_congestion']
                    weekly_change = shipping_data['weekly_change_pct']
                    
                    # Color based on sentiment (for shipping, lower congestion is positive)
                    color = {
                        'positive': 'green',
                        'negative': 'red',
                        'neutral': 'gray'
                    }[shipping_data['sentiment']]
                    
                    st.markdown(
                        f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px;'>"
                        f"<h3>Global Shipping Congestion</h3>"
                        f"<p style='font-size:2em; margin:5px 0;'>{current_congestion:.1f}%</p>"
                        f"<p>Weekly change: <span style='color:{color}'>{'↑' if weekly_change > 0 else '↓'} {abs(weekly_change):.1f}%</span></p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Insight card
                    st.markdown(
                        f"<div style='background-color:rgba({{'green': '76, 175, 80', 'red': '244, 67, 54', 'gray': '158, 158, 158'}}['{color}'], 0.1); padding:10px; border-left:3px solid {{'green': '#4CAF50', 'red': '#F44336', 'gray': '#9E9E9E'}}['{color}']; margin-top:10px;'>"
                        f"<h4 style='margin:0;'>Key Insight</h4>"
                        f"<p>{shipping_data['insight']}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                
                with col2:
                    # Overall congestion trend chart
                    fig = go.Figure()
                    
                    # Add congestion line
                    fig.add_trace(go.Scatter(
                        x=shipping_data['dates'],
                        y=shipping_data['overall_congestion'],
                        mode='lines+markers',
                        name='Global Congestion',
                        line=dict(color='#1E88E5', width=2),
                        marker=dict(size=5)
                    ))
                    
                    # Add trend line (7-day moving average)
                    ma_window = min(7, len(shipping_data['overall_congestion']))
                    congestion_ma = pd.Series(shipping_data['overall_congestion']).rolling(window=ma_window).mean()
                    
                    fig.add_trace(go.Scatter(
                        x=shipping_data['dates'],
                        y=congestion_ma,
                        mode='lines',
                        name='7-day Trend',
                        line=dict(color='#FF9800', width=1.5, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title='Global Shipping Congestion Trend',
                        xaxis_title='Date',
                        yaxis_title='Congestion (%)',
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Shipping routes analysis
                st.subheader("Shipping Routes Analysis")
                
                # Create route selection
                routes = shipping_data['routes']
                selected_routes = st.multiselect(
                    "Select Shipping Routes",
                    options=routes,
                    default=routes[:3]  # Default to first 3 routes
                )
                
                if selected_routes:
                    # Create congestion chart for selected routes
                    fig = go.Figure()
                    
                    for route in selected_routes:
                        route_index = routes.index(route)
                        route_data = shipping_data['route_data'][route]
                        
                        fig.add_trace(go.Scatter(
                            x=shipping_data['dates'],
                            y=route_data,
                            mode='lines',
                            name=route
                        ))
                    
                    fig.update_layout(
                        title='Shipping Congestion by Route',
                        xaxis_title='Date',
                        yaxis_title='Congestion (%)',
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Please select at least one shipping route to display")
                
                # Impact on specific stocks
                st.subheader("Supply Chain Impact on Stocks")
                
                # Map of stocks affected by shipping congestion
                affected_stocks = {
                    "retail": ["AMZN", "WMT", "TGT", "COST"],
                    "tech": ["AAPL", "MSFT", "DELL", "HPQ"],
                    "automotive": ["TSLA", "F", "GM", "TM"],
                    "manufacturing": ["CAT", "DE", "GE", "BA"]
                }
                
                # Choose a relevant sector for the current ticker
                if ticker in affected_stocks["retail"]:
                    relevant_sector = "retail"
                elif ticker in affected_stocks["tech"]:
                    relevant_sector = "tech"
                elif ticker in affected_stocks["automotive"]:
                    relevant_sector = "automotive"
                elif ticker in affected_stocks["manufacturing"]:
                    relevant_sector = "manufacturing"
                else:
                    # Default to retail if we don't have a mapping
                    relevant_sector = "retail"
                
                # Display relevant stocks in the same sector
                st.markdown(f"### Stocks in the {relevant_sector.capitalize()} Sector")
                
                # Create columns for each relevant stock
                cols = st.columns(len(affected_stocks[relevant_sector]))
                
                for i, related_ticker in enumerate(affected_stocks[relevant_sector]):
                    impact_level = np.random.uniform(0.5, 5.0)  # Random impact level for demonstration
                    impact_text = "High" if impact_level > 3.5 else "Medium" if impact_level > 2.0 else "Low"
                    impact_color = "red" if impact_level > 3.5 else "orange" if impact_level > 2.0 else "green"
                    
                    with cols[i]:
                        st.markdown(
                            f"<div style='text-align:center; padding:10px; border:1px solid #f0f0f0; border-radius:5px;'>"
                            f"<h4>{related_ticker}</h4>"
                            f"<p>Supply Chain Impact:</p>"
                            f"<p style='font-size:1.2em; color:{impact_color};'>{impact_text}</p>"
                            f"<p>Score: {impact_level:.1f}/5.0</p>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                
                # About the data
                st.markdown("""
                **About this data:** This analysis is based on simulated global shipping congestion data. 
                In a real-world scenario, this data would be derived from maritime tracking systems, 
                port authority reports, and other logistics information to measure supply chain disruptions 
                and their potential impact on company operations and stock performance.
                """)
            else:
                st.warning("No shipping data available for analysis")
        
        with tab3:
            # Consumer Spending Analysis
            st.subheader("Consumer Spending Analysis")
            
            # Time period selection
            spending_period = st.selectbox(
                "Analysis Timeframe",
                ["90 days", "180 days", "365 days"],
                index=0,
                key="spending_period"
            )
            
            # Convert period to number of days
            spending_days = int(spending_period.split()[0])
            
            # Fetch spending data
            spending_data = generate_credit_card_spending_data(ticker, days=spending_days)
            
            if spending_data:
                # Display spending overview
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Current spending metric
                    current_spending = spending_data['current_spending_avg']
                    weekly_change = spending_data['weekly_change_pct']
                    category = spending_data['category']
                    
                    # Color based on sentiment
                    color = {
                        'positive': 'green',
                        'negative': 'red',
                        'neutral': 'gray'
                    }[spending_data['sentiment']]
                    
                    st.markdown(
                        f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px;'>"
                        f"<h3>{category} Spending</h3>"
                        f"<p style='font-size:2em; margin:5px 0;'>{current_spending:.1f}</p>"
                        f"<p>Weekly change: <span style='color:{color}'>{'↑' if weekly_change > 0 else '↓'} {abs(weekly_change):.1f}%</span></p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Insight card
                    st.markdown(
                        f"<div style='background-color:rgba({{'green': '76, 175, 80', 'red': '244, 67, 54', 'gray': '158, 158, 158'}}['{color}'], 0.1); padding:10px; border-left:3px solid {{'green': '#4CAF50', 'red': '#F44336', 'gray': '#9E9E9E'}}['{color}']; margin-top:10px;'>"
                        f"<h4 style='margin:0;'>Key Insight</h4>"
                        f"<p>{spending_data['insight']}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # YoY change if available
                    if spending_data.get('yoy_change_pct') is not None:
                        yoy_change = spending_data['yoy_change_pct']
                        yoy_color = "green" if yoy_change > 0 else "red"
                        
                        st.markdown(
                            f"<div style='padding:10px; border:1px solid #f0f0f0; border-radius:5px; margin-top:10px;'>"
                            f"<h4>Year-over-Year Change</h4>"
                            f"<p style='font-size:1.5em; color:{yoy_color};'>{'↑' if yoy_change > 0 else '↓'} {abs(yoy_change):.1f}%</p>"
                            f"<p>{spending_data.get('yoy_insight', '')}</p>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                
                with col2:
                    # Spending trend chart
                    fig = go.Figure()
                    
                    # Add spending line
                    fig.add_trace(go.Scatter(
                        x=spending_data['dates'],
                        y=spending_data['spending'],
                        mode='lines',
                        name='Spending',
                        line=dict(color='#1E88E5', width=2)
                    ))
                    
                    # Add trend line (14-day moving average)
                    ma_window = min(14, len(spending_data['spending']))
                    spending_ma = pd.Series(spending_data['spending']).rolling(window=ma_window).mean()
                    
                    fig.add_trace(go.Scatter(
                        x=spending_data['dates'],
                        y=spending_ma,
                        mode='lines',
                        name='14-day Trend',
                        line=dict(color='#FF9800', width=1.5, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f'{category} Spending Trend',
                        xaxis_title='Date',
                        yaxis_title='Spending Index',
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Spending vs. Stock Price
                st.subheader("Consumer Spending vs. Stock Price")
                
                # Fetch stock price data
                price_period = "1y" if spending_days > 180 else "6mo" if spending_days > 90 else "3mo"
                stock_data = get_stock_data(ticker, period=price_period)
                
                if stock_data is not None and not stock_data.empty:
                    # Create a figure with dual axes
                    fig = go.Figure()
                    
                    # Add stock price
                    fig.add_trace(go.Scatter(
                        x=stock_data.index,
                        y=stock_data['Close'],
                        mode='lines',
                        name='Stock Price',
                        line=dict(color='#1E88E5', width=2),
                        yaxis='y'
                    ))
                    
                    # Convert spending data dates to datetime
                    spending_dates = [datetime.strptime(d, '%Y-%m-%d') for d in spending_data['dates']]
                    
                    # Add spending data
                    fig.add_trace(go.Scatter(
                        x=spending_dates,
                        y=spending_data['spending'],
                        mode='lines',
                        name=f'{category} Spending',
                        line=dict(color='#4CAF50', width=1.5),
                        yaxis='y2'
                    ))
                    
                    fig.update_layout(
                        title=f'{ticker} Price vs. {category} Spending',
                        xaxis_title='Date',
                        yaxis_title='Price (₹)',
                        yaxis2=dict(
                            title='Spending Index',
                            titlefont=dict(color='rgba(76, 175, 80, 0.8)'),
                            tickfont=dict(color='rgba(76, 175, 80, 0.8)'),
                            overlaying='y',
                            side='right',
                            showgrid=False
                        ),
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate correlation if we have enough data
                    if len(spending_data['spending']) > 5 and len(stock_data) > 5:
                        # Sample down to aligned dates
                        spending_df = pd.DataFrame({
                            'Date': spending_dates,
                            'Spending': spending_data['spending']
                        })
                        
                        price_df = pd.DataFrame({
                            'Date': stock_data.index,
                            'Price': stock_data['Close']
                        })
                        
                        # Merge based on nearest dates
                        merged_df = pd.merge_asof(
                            spending_df.sort_values('Date'),
                            price_df.sort_values('Date'),
                            on='Date',
                            direction='nearest'
                        )
                        
                        if len(merged_df) > 5:
                            correlation = merged_df['Spending'].corr(merged_df['Price'])
                            
                            # Display correlation
                            st.markdown(
                                f"<div style='text-align:center; padding:10px; background-color:rgba(0,0,0,0.05); border-radius:5px;'>"
                                f"<h4>Correlation between {category} Spending and Stock Price</h4>"
                                f"<p style='font-size:1.5em; margin:5px 0;'>{correlation:.2f}</p>"
                                f"<p>{interpret_correlation(correlation)}</p>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                            # Calculate lead/lag relationships
                            st.subheader("Lead/Lag Analysis")
                            
                            # Calculate correlations for different lags (spending leading price)
                            lag_correlations = []
                            max_lag = min(30, len(merged_df) // 3)
                            
                            for lag in range(-max_lag, max_lag + 1):
                                if lag == 0:
                                    # We already calculated this
                                    lag_correlations.append((lag, correlation))
                                else:
                                    # Shift spending data to test different lead/lag relationships
                                    merged_df[f'Spending_Lag_{lag}'] = merged_df['Spending'].shift(lag)
                                    lag_corr = merged_df['Price'].corr(merged_df[f'Spending_Lag_{lag}'])
                                    lag_correlations.append((lag, lag_corr))
                            
                            # Create DataFrame for plotting
                            lag_df = pd.DataFrame(lag_correlations, columns=['Lag', 'Correlation'])
                            
                            # Plot the lead/lag correlations
                            fig = px.line(
                                lag_df,
                                x='Lag',
                                y='Correlation',
                                title='Lead/Lag Relationship between Spending and Stock Price',
                                labels={'Lag': 'Days (Negative = Spending Leads, Positive = Price Leads)', 'Correlation': 'Correlation'}
                            )
                            
                            fig.add_shape(
                                type="line",
                                x0=lag_df['Lag'].min(),
                                y0=0,
                                x1=lag_df['Lag'].max(),
                                y1=0,
                                line=dict(
                                    color="gray",
                                    width=1,
                                    dash="dash",
                                )
                            )
                            
                            fig.update_layout(
                                height=350,
                                margin=dict(l=0, r=0, t=30, b=0)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Find the peak correlation
                            max_corr_lag = lag_df.loc[lag_df['Correlation'].abs().idxmax()]
                            
                            if max_corr_lag['Lag'] < 0:
                                lag_insight = f"**Spending data tends to lead price movements by {-int(max_corr_lag['Lag'])} days** with a correlation of {max_corr_lag['Correlation']:.2f}."
                            elif max_corr_lag['Lag'] > 0:
                                lag_insight = f"**Price movements tend to lead spending data by {int(max_corr_lag['Lag'])} days** with a correlation of {max_corr_lag['Correlation']:.2f}."
                            else:
                                lag_insight = "**No significant lead/lag relationship** was found between spending data and price movements."
                            
                            st.markdown(lag_insight)
                else:
                    st.warning(f"Unable to fetch price data for {ticker}")
                
                # About the data
                st.markdown("""
                **About this data:** This analysis is based on simulated credit card spending data. 
                In a real-world scenario, this data would be derived from anonymized credit card 
                transaction records, providing insights into consumer spending patterns across 
                different categories and their relationship to company performance.
                """)
            else:
                st.warning(f"No consumer spending data available for {ticker}")
                
        with tab4:
            # Agricultural Satellite Imagery Analysis
            st.subheader("Agricultural Satellite Imagery Analysis")
            
            # Time period selection
            agri_period = st.selectbox(
                "Analysis Timeframe",
                ["30 days", "60 days", "90 days"],
                index=2,
                key="agri_period"
            )
            
            # Convert period to number of days
            agri_days = int(agri_period.split()[0])
            
            # Fetch agricultural satellite data
            agri_data = generate_agricultural_satellite_data(ticker, days=agri_days)
            
            if agri_data:
                # Display crop overview
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Current NDVI metric
                    crop_type = agri_data['crop_type']
                    current_ndvi = agri_data['current_avg_ndvi']
                    ndvi_change = agri_data['ndvi_change_pct']
                    
                    # Color based on sentiment
                    color = {
                        'positive': 'green',
                        'negative': 'red',
                        'neutral': 'gray'
                    }[agri_data['sentiment']]
                    
                    st.markdown(
                        f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px;'>"
                        f"<h3>{crop_type} Health</h3>"
                        f"<p style='font-size:2em; margin:5px 0;'>{current_ndvi:.2f}</p>"
                        f"<p>NDVI Index (0-1 scale)</p>"
                        f"<p>Weekly change: <span style='color:{color}'>{'↑' if ndvi_change > 0 else '↓'} {abs(ndvi_change):.1f}%</span></p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Insight card
                    st.markdown(
                        f"<div style='background-color:rgba({{'green': '76, 175, 80', 'red': '244, 67, 54', 'gray': '158, 158, 158'}}['{color}'], 0.1); padding:10px; border-left:3px solid {{'green': '#4CAF50', 'red': '#F44336', 'gray': '#9E9E9E'}}['{color}']; margin-top:10px;'>"
                        f"<h4 style='margin:0;'>Key Insight</h4>"
                        f"<p>{agri_data['insight']}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Yield prediction
                    st.markdown(
                        f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px; margin-top:15px;'>"
                        f"<h4>Yield Prediction</h4>"
                        f"<p><b>{agri_data['predicted_yield']:.2f}</b> tonnes/hectare</p>"
                        f"<p>Total Production: <b>{agri_data['total_production']/1000000:.2f}</b> million tonnes</p>"
                        f"<p>Based on {agri_data['crop_area']:.0f} thousand hectares</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                
                with col2:
                    # NDVI Trend Chart
                    fig = go.Figure()
                    
                    # Add NDVI line
                    fig.add_trace(go.Scatter(
                        x=agri_data['dates'],
                        y=agri_data['ndvi_values'],
                        mode='lines+markers',
                        name='NDVI Index',
                        line=dict(color='#4CAF50', width=2),
                        marker=dict(size=5)
                    ))
                    
                    # Add trend line (7-day moving average)
                    ma_window = min(7, len(agri_data['ndvi_values']))
                    ndvi_ma = pd.Series(agri_data['ndvi_values']).rolling(window=ma_window).mean()
                    
                    fig.add_trace(go.Scatter(
                        x=agri_data['dates'],
                        y=ndvi_ma,
                        mode='lines',
                        name='7-day Trend',
                        line=dict(color='#FF9800', width=1.5, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f'Vegetation Health (NDVI) Trend for {crop_type}',
                        xaxis_title='Date',
                        yaxis_title='NDVI Index (0-1)',
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Soil Moisture Analysis
                st.subheader("Soil Moisture Analysis")
                
                # Create soil moisture chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=agri_data['dates'],
                    y=agri_data['soil_moisture'],
                    mode='lines',
                    name='Soil Moisture',
                    line=dict(color='#2196F3', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(33, 150, 243, 0.1)'
                ))
                
                # Add optimal moisture range
                optimal_lower = [40] * len(agri_data['dates'])
                optimal_upper = [70] * len(agri_data['dates'])
                
                fig.add_trace(go.Scatter(
                    x=agri_data['dates'],
                    y=optimal_upper,
                    mode='lines',
                    name='Optimal Range (Upper)',
                    line=dict(color='rgba(76, 175, 80, 0.5)', width=1, dash='dash')
                ))
                
                fig.add_trace(go.Scatter(
                    x=agri_data['dates'],
                    y=optimal_lower,
                    mode='lines',
                    name='Optimal Range (Lower)',
                    line=dict(color='rgba(76, 175, 80, 0.5)', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(76, 175, 80, 0.1)'
                ))
                
                fig.update_layout(
                    title='Soil Moisture Levels',
                    xaxis_title='Date',
                    yaxis_title='Moisture (%)',
                    height=350,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # NDVI vs LAI Comparison
                st.subheader("Vegetation Indices Comparison")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # NDVI Distribution
                    fig = px.histogram(
                        x=agri_data['ndvi_values'],
                        nbins=20,
                        title='NDVI Distribution',
                        labels={'x': 'NDVI Value'},
                        color_discrete_sequence=['#4CAF50']
                    )
                    
                    fig.update_layout(
                        height=250,
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # LAI Distribution
                    fig = px.histogram(
                        x=agri_data['lai_values'],
                        nbins=20,
                        title='LAI Distribution',
                        labels={'x': 'LAI Value'},
                        color_discrete_sequence=['#2196F3']
                    )
                    
                    fig.update_layout(
                        height=250,
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # About the data
                st.markdown("""
                **About this data:** This analysis is based on simulated satellite imagery data for agricultural 
                monitoring. In a real-world scenario, this data would be derived from actual satellite imagery 
                using vegetation indices like NDVI (Normalized Difference Vegetation Index) and LAI (Leaf Area Index).
                
                These indices allow analysts to monitor crop health, predict yields, and assess agricultural 
                production at regional and national scales, providing valuable insights for stocks in the 
                agricultural sector.
                """)
            else:
                st.info(f"No agricultural satellite data available for {ticker}. This data is most relevant for companies in the agricultural, food production, and related sectors.")
                
        with tab5:
            # Weather Impact Analysis
            st.subheader("Weather & Climate Impact Analysis")
            
            # Time period selection
            weather_period = st.selectbox(
                "Analysis Timeframe",
                ["30 days", "60 days", "90 days"],
                index=2,
                key="weather_period"
            )
            
            # Convert period to number of days
            weather_days = int(weather_period.split()[0])
            
            # Fetch weather impact data
            weather_data = generate_weather_impact_data(ticker, days=weather_days)
            
            if weather_data:
                # Display crop category and health overview
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Current crop health metric
                    category = weather_data['category']
                    current_health = weather_data['current_health_avg']
                    weekly_change = weather_data['weekly_change_pct']
                    
                    # Color based on sentiment
                    color = {
                        'positive': 'green',
                        'negative': 'red',
                        'neutral': 'gray'
                    }[weather_data['sentiment']]
                    
                    st.markdown(
                        f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px;'>"
                        f"<h3>{category} Health</h3>"
                        f"<p style='font-size:2em; margin:5px 0;'>{current_health:.1f}</p>"
                        f"<p>Health Index (0-100 scale)</p>"
                        f"<p>Weekly change: <span style='color:{color}'>{'↑' if weekly_change > 0 else '↓'} {abs(weekly_change):.1f}%</span></p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Insight card
                    st.markdown(
                        f"<div style='background-color:rgba({{'green': '76, 175, 80', 'red': '244, 67, 54', 'gray': '158, 158, 158'}}['{color}'], 0.1); padding:10px; border-left:3px solid {{'green': '#4CAF50', 'red': '#F44336', 'gray': '#9E9E9E'}}['{color}']; margin-top:10px;'>"
                        f"<h4 style='margin:0;'>Key Insight</h4>"
                        f"<p>{weather_data['insight']}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Company Impact
                    impact_factor = weather_data['weather_impact_factor']
                    impact_color = 'red' if impact_factor > 0.3 else 'orange' if impact_factor > 0.1 else 'green'
                    
                    st.markdown(
                        f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px; margin-top:15px;'>"
                        f"<h4>Company Impact Assessment</h4>"
                        f"<p style='font-size:1.5em; color:{impact_color};'>{impact_factor:.2f}</p>"
                        f"<p>Impact Factor (0-1 scale)</p>"
                        f"<p>{'High' if impact_factor > 0.3 else 'Medium' if impact_factor > 0.1 else 'Low'} sensitivity to weather conditions</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                
                with col2:
                    # Crop Health Trend Chart
                    fig = go.Figure()
                    
                    # Add health index line
                    fig.add_trace(go.Scatter(
                        x=weather_data['dates'],
                        y=weather_data['crop_health'],
                        mode='lines',
                        name='Crop Health',
                        line=dict(color='#4CAF50', width=2)
                    ))
                    
                    # Add trend line (7-day moving average)
                    ma_window = min(7, len(weather_data['crop_health']))
                    health_ma = pd.Series(weather_data['crop_health']).rolling(window=ma_window).mean()
                    
                    fig.add_trace(go.Scatter(
                        x=weather_data['dates'],
                        y=health_ma,
                        mode='lines',
                        name='7-day Trend',
                        line=dict(color='#FF9800', width=1.5, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f'Crop Health Trend for {category}',
                        xaxis_title='Date',
                        yaxis_title='Health Index (0-100)',
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Weather Patterns Analysis
                st.subheader("Weather Patterns Analysis")
                
                # Create rainfall and temperature chart
                fig = go.Figure()
                
                # Add rainfall data
                fig.add_trace(go.Bar(
                    x=weather_data['dates'],
                    y=weather_data['rainfall'],
                    name='Rainfall (mm)',
                    marker_color='rgba(33, 150, 243, 0.7)'
                ))
                
                # Add temperature data on secondary y-axis
                fig.add_trace(go.Scatter(
                    x=weather_data['dates'],
                    y=weather_data['temperature'],
                    mode='lines',
                    name='Temperature (°C)',
                    line=dict(color='#FF5722', width=2),
                    yaxis='y2'
                ))
                
                # Update layout with secondary y-axis
                fig.update_layout(
                    title='Rainfall & Temperature Patterns',
                    xaxis_title='Date',
                    yaxis_title='Rainfall (mm)',
                    yaxis2=dict(
                        title='Temperature (°C)',
                        titlefont=dict(color='#FF5722'),
                        tickfont=dict(color='#FF5722'),
                        overlaying='y',
                        side='right',
                        showgrid=False
                    ),
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=0),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Extreme Weather Events
                if weather_data['extreme_events']:
                    st.subheader("Extreme Weather Events")
                    
                    events_df = pd.DataFrame(weather_data['extreme_events'])
                    
                    # Format severity as percentage
                    events_df['Severity'] = events_df['severity'].apply(lambda x: f"{int(x*100)}%")
                    
                    # Rename columns for display
                    events_df = events_df.rename(columns={
                        'date': 'Date',
                        'type': 'Event Type'
                    })[['Date', 'Event Type', 'Severity']]
                    
                    st.table(events_df)
                    
                    st.markdown("""
                    **Note:** Extreme weather events can significantly impact agricultural production, 
                    supply chains, and overall business operations. For companies with high weather sensitivity,
                    these events may have material impacts on financial performance.
                    """)
                
                # About the data
                st.markdown("""
                **About this data:** This analysis is based on simulated weather and climate data relevant to 
                agricultural and weather-sensitive sectors. In a real-world scenario, this data would be derived 
                from actual weather stations, meteorological satellites, and climate models.
                
                The analysis evaluates both current conditions and historic patterns to assess crop health and 
                potential weather-related risks for companies with exposure to weather-sensitive sectors.
                """)
            else:
                st.info(f"No weather impact data available for {ticker}. This data is most relevant for companies in the agricultural, energy, transportation, and other weather-sensitive sectors.")
                
        with tab6:
            # Social Media Trends Analysis
            st.subheader("Social Media & Web Trends Analysis")
            
            # Time period selection
            social_period = st.selectbox(
                "Analysis Timeframe",
                ["30 days", "60 days", "90 days"],
                index=0,
                key="social_period"
            )
            
            # Convert period to number of days
            social_days = int(social_period.split()[0])
            
            # Fetch social media data
            social_data = generate_social_media_trends(ticker, days=social_days)
            
            if social_data:
                # Display sentiment and mention overview
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Current sentiment metric
                    current_sentiment = social_data['avg_sentiment']
                    sentiment_change = social_data['sentiment_change']
                    mention_change = social_data['mention_change_pct']
                    
                    # Color based on sentiment
                    color = 'green' if current_sentiment > 0.2 else 'red' if current_sentiment < -0.1 else 'gray'
                    
                    # Sentiment classification
                    sentiment_label = 'Positive' if current_sentiment > 0.2 else 'Negative' if current_sentiment < -0.1 else 'Neutral'
                    
                    st.markdown(
                        f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px;'>"
                        f"<h3>Social Sentiment</h3>"
                        f"<p style='font-size:2em; margin:5px 0; color:{color};'>{sentiment_label}</p>"
                        f"<p>Sentiment Score: {current_sentiment:.2f} (-1 to 1 scale)</p>"
                        f"<p>Weekly change: <span style='color:{'green' if sentiment_change > 0 else 'red' if sentiment_change < 0 else 'gray'}'>{'↑' if sentiment_change > 0 else '↓' if sentiment_change < 0 else '–'} {abs(sentiment_change):.2f}</span></p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Mention Volume
                    st.markdown(
                        f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px; margin-top:15px;'>"
                        f"<h3>Mention Volume</h3>"
                        f"<p style='font-size:2em; margin:5px 0;'>{int(social_data['avg_mentions'])}</p>"
                        f"<p>Daily Average</p>"
                        f"<p>Weekly change: <span style='color:{'green' if mention_change > 0 else 'red' if mention_change < 0 else 'gray'}'>{'↑' if mention_change > 0 else '↓' if mention_change < 0 else '–'} {abs(mention_change):.1f}%</span></p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Insight card
                    st.markdown(
                        f"<div style='background-color:rgba({{'green': '76, 175, 80', 'red': '244, 67, 54', 'gray': '158, 158, 158'}}['{color}'], 0.1); padding:10px; border-left:3px solid {{'green': '#4CAF50', 'red': '#F44336', 'gray': '#9E9E9E'}}['{color}']; margin-top:15px;'>"
                        f"<h4 style='margin:0;'>Key Insight</h4>"
                        f"<p>{social_data['insight']}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                
                with col2:
                    # Create tabs for different social metrics
                    social_subtabs = st.tabs(["Sentiment Trend", "Mention Volume", "Engagement"])
                    
                    with social_subtabs[0]:
                        # Sentiment trend chart
                        fig = go.Figure()
                        
                        # Add sentiment line
                        fig.add_trace(go.Scatter(
                            x=social_data['dates'],
                            y=social_data['sentiment_scores'],
                            mode='lines',
                            name='Sentiment Score',
                            line=dict(color='#1E88E5', width=2)
                        ))
                        
                        # Add trend line (7-day moving average)
                        ma_window = min(7, len(social_data['sentiment_scores']))
                        sentiment_ma = pd.Series(social_data['sentiment_scores']).rolling(window=ma_window).mean()
                        
                        fig.add_trace(go.Scatter(
                            x=social_data['dates'],
                            y=sentiment_ma,
                            mode='lines',
                            name='7-day Trend',
                            line=dict(color='#FF9800', width=1.5, dash='dash')
                        ))
                        
                        # Add zero line for reference
                        fig.add_shape(
                            type="line",
                            x0=social_data['dates'][0],
                            y0=0,
                            x1=social_data['dates'][-1],
                            y1=0,
                            line=dict(color="rgba(0,0,0,0.2)", width=1, dash="dot")
                        )
                        
                        fig.update_layout(
                            title='Social Media Sentiment Trend',
                            xaxis_title='Date',
                            yaxis_title='Sentiment Score (-1 to 1)',
                            height=300,
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with social_subtabs[1]:
                        # Mention volume chart
                        fig = go.Figure()
                        
                        # Add mention volume line
                        fig.add_trace(go.Scatter(
                            x=social_data['dates'],
                            y=social_data['mention_volume'],
                            mode='lines',
                            name='Mention Volume',
                            line=dict(color='#7B1FA2', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(123, 31, 162, 0.1)'
                        ))
                        
                        # Add trend line (7-day moving average)
                        ma_window = min(7, len(social_data['mention_volume']))
                        mention_ma = pd.Series(social_data['mention_volume']).rolling(window=ma_window).mean()
                        
                        fig.add_trace(go.Scatter(
                            x=social_data['dates'],
                            y=mention_ma,
                            mode='lines',
                            name='7-day Trend',
                            line=dict(color='#FF9800', width=1.5, dash='dash')
                        ))
                        
                        fig.update_layout(
                            title='Social Media Mention Volume',
                            xaxis_title='Date',
                            yaxis_title='Daily Mentions',
                            height=300,
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with social_subtabs[2]:
                        # Engagement rate chart
                        fig = go.Figure()
                        
                        # Add engagement rate line
                        fig.add_trace(go.Scatter(
                            x=social_data['dates'],
                            y=social_data['engagement_rates'],
                            mode='lines',
                            name='Engagement Rate',
                            line=dict(color='#009688', width=2)
                        ))
                        
                        # Add search trend line (on secondary y-axis)
                        fig.add_trace(go.Scatter(
                            x=social_data['dates'],
                            y=social_data['search_trends'],
                            mode='lines',
                            name='Search Trend',
                            line=dict(color='#FFC107', width=2),
                            yaxis='y2'
                        ))
                        
                        fig.update_layout(
                            title='Engagement Rates & Search Trends',
                            xaxis_title='Date',
                            yaxis_title='Engagement Rate (%)',
                            yaxis2=dict(
                                title='Search Trend Index',
                                titlefont=dict(color='#FFC107'),
                                tickfont=dict(color='#FFC107'),
                                overlaying='y',
                                side='right',
                                showgrid=False
                            ),
                            height=300,
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                # Anomaly Detection
                if social_data['anomalies']:
                    st.subheader("Social Media Anomalies Detected")
                    
                    anomalies_df = pd.DataFrame(social_data['anomalies'])
                    
                    # Format magnitude
                    anomalies_df['Magnitude'] = anomalies_df['magnitude'].apply(lambda x: f"{x:.2f}")
                    
                    # Rename columns for display
                    anomalies_df = anomalies_df.rename(columns={
                        'date': 'Date',
                        'type': 'Type',
                        'description': 'Description'
                    })[['Date', 'Type', 'Magnitude', 'Description']]
                    
                    st.table(anomalies_df)
                    
                    st.markdown("""
                    **Note:** Social media anomalies can indicate important events affecting company perception. 
                    Sudden increases in mention volume or shifts in sentiment may correlate with news events, 
                    product launches, controversies, or other market-moving developments.
                    """)
                
                # Topic Distribution
                st.subheader("Topic Distribution")
                
                topic_df = pd.DataFrame({
                    'Topic': list(social_data['topic_distribution'].keys()),
                    'Percentage': list(social_data['topic_distribution'].values())
                })
                
                fig = px.pie(
                    topic_df,
                    values='Percentage',
                    names='Topic',
                    title='Social Media Topic Distribution',
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                
                fig.update_layout(
                    height=350,
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Mobile Location Data (if available)
                mobile_data = generate_mobile_location_data(ticker)
                
                if mobile_data:
                    st.subheader("Mobile Location Intelligence")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Traffic and conversion metrics
                        st.markdown(
                            f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px;'>"
                            f"<h4>Store Traffic</h4>"
                            f"<p style='font-size:1.5em; margin:5px 0;'>{int(mobile_data['avg_traffic'])}</p>"
                            f"<p>Daily Average Visitors</p>"
                            f"<p>Weekly change: <span style='color:{'green' if mobile_data['traffic_change_pct'] > 0 else 'red' if mobile_data['traffic_change_pct'] < 0 else 'gray'}'>{'↑' if mobile_data['traffic_change_pct'] > 0 else '↓' if mobile_data['traffic_change_pct'] < 0 else '–'} {abs(mobile_data['traffic_change_pct']):.1f}%</span></p>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        
                        # Insight card
                        st.markdown(
                            f"<div style='background-color:rgba({{'green': '76, 175, 80', 'red': '244, 67, 54', 'gray': '158, 158, 158'}}['{mobile_data['sentiment']}'], 0.1); padding:10px; border-left:3px solid {{'green': '#4CAF50', 'red': '#F44336', 'gray': '#9E9E9E'}}['{mobile_data['sentiment']}']; margin-top:10px;'>"
                            f"<h4 style='margin:0;'>Location Insight</h4>"
                            f"<p>{mobile_data['insight']}</p>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    
                    with col2:
                        # Create foot traffic chart
                        fig = go.Figure()
                        
                        # Add foot traffic line
                        fig.add_trace(go.Scatter(
                            x=mobile_data['dates'],
                            y=mobile_data['foot_traffic'],
                            mode='lines',
                            name='Foot Traffic',
                            line=dict(color='#5E35B1', width=2)
                        ))
                        
                        # Add conversion rate line (on secondary y-axis)
                        fig.add_trace(go.Scatter(
                            x=mobile_data['dates'],
                            y=mobile_data['conversion_rates'],
                            mode='lines',
                            name='Conversion Rate (%)',
                            line=dict(color='#00BCD4', width=2),
                            yaxis='y2'
                        ))
                        
                        fig.update_layout(
                            title='Store Foot Traffic & Conversion Rates',
                            xaxis_title='Date',
                            yaxis_title='Daily Visitors',
                            yaxis2=dict(
                                title='Conversion Rate (%)',
                                titlefont=dict(color='#00BCD4'),
                                tickfont=dict(color='#00BCD4'),
                                overlaying='y',
                                side='right',
                                showgrid=False
                            ),
                            height=300,
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Location Heatmap
                    st.subheader("Store Traffic by Location")
                    
                    location_df = pd.DataFrame({
                        'City': list(mobile_data['location_heatmap'].keys()),
                        'Percentage': list(mobile_data['location_heatmap'].values())
                    }).sort_values('Percentage', ascending=False)
                    
                    fig = px.bar(
                        location_df,
                        x='City',
                        y='Percentage',
                        title='Foot Traffic Distribution by City',
                        color='Percentage',
                        color_continuous_scale='Viridis'
                    )
                    
                    fig.update_layout(
                        height=300,
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Cross-shopping Analysis
                    st.subheader("Cross-Shopping Analysis")
                    
                    cross_df = pd.DataFrame({
                        'Retailer': list(mobile_data['cross_shopping'].keys()),
                        'Percentage': list(mobile_data['cross_shopping'].values())
                    }).sort_values('Percentage', ascending=False)
                    
                    fig = px.bar(
                        cross_df,
                        x='Retailer',
                        y='Percentage',
                        title='Cross-Shopping Behavior (% of customers who also shop at)',
                        color='Percentage',
                        color_continuous_scale='Oranges'
                    )
                    
                    fig.update_layout(
                        height=300,
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # About the data
                st.markdown("""
                **About this data:** This analysis is based on simulated social media and web data. 
                In a real-world scenario, this data would be derived from actual social media platforms, 
                search engines, and mobile location intelligence providers.
                
                These alternative data sources can provide early signals of shifting consumer sentiment, 
                brand perception, and physical store traffic patterns, which may impact company performance 
                before being reflected in traditional financial metrics.
                """)
            else:
                st.info(f"No social media trend data available for {ticker}. This data is most relevant for consumer-facing companies with significant brand presence.")
    else:
        st.error(f"Unable to fetch data for ticker: {ticker}. Please enter a valid ticker symbol.")
    
    # Additional Information
    st.markdown("---")
    st.markdown("""
    ### About Alternative Data Analysis
    
    This page analyzes alternative data sources that can provide insights beyond traditional financial metrics:
    
    1. **Retail/Manufacturing Activity** - Examines foot traffic or manufacturing activity derived from satellite imagery.
    
    2. **Shipping & Supply Chain** - Monitors global shipping congestion and supply chain disruptions.
    
    3. **Consumer Spending** - Tracks consumer spending patterns in relevant categories.
    
    *Note: Alternative data can provide unique insights not yet reflected in stock prices, but should be used alongside traditional analysis methods.*
    """)

def interpret_correlation(correlation):
    """
    Interpret correlation values
    
    Parameters:
    correlation (float): Correlation coefficient
    
    Returns:
    str: Interpretation of correlation
    """
    abs_corr = abs(correlation)
    
    if abs_corr < 0.3:
        strength = "Weak"
    elif abs_corr < 0.5:
        strength = "Moderate"
    elif abs_corr < 0.7:
        strength = "Strong"
    else:
        strength = "Very strong"
    
    if correlation > 0:
        direction = "positive"
        explanation = "the metrics tend to move in the same direction"
    else:
        direction = "negative"
        explanation = "the metrics tend to move in opposite directions"
    
    return f"{strength} {direction} correlation ({explanation})"
