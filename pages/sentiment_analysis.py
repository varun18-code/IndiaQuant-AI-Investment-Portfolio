import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.stock_data import get_stock_data, get_stock_info
from utils.sentiment_analysis import (
    SentimentAnalyzer,
    fetch_financial_news,
    analyze_news_sentiment,
    fetch_social_media_sentiment
)

def show():
    """Display the sentiment analysis page"""
    st.header("Sentiment Analysis")
    
    # Default ticker
    default_ticker = "AAPL"
    
    # Select stock
    ticker = st.text_input("Enter Ticker Symbol", value=default_ticker).upper()
    
    # Fetch stock info
    stock_info = get_stock_info(ticker)
    
    if stock_info and stock_info.get('shortName') != 'N/A':
        # Stock name and basic info
        st.subheader(f"{stock_info['shortName']} ({ticker}) Sentiment Analysis")
        
        # Create tabs for different sentiment analyses
        tab1, tab2, tab3 = st.tabs(["News Sentiment", "Social Media Sentiment", "Sentiment Trends"])
        
        with tab1:
            # News sentiment analysis
            st.subheader("Financial News Sentiment")
            
            # Time period selection for news
            news_period = st.selectbox(
                "News Timeframe",
                ["7 days", "14 days", "30 days"],
                index=0
            )
            
            # Convert period to number of days
            days = int(news_period.split()[0])
            
            # Fetch news
            with st.spinner("Fetching and analyzing news..."):
                news_items = fetch_financial_news(ticker, days=days, max_results=20)
            
            if news_items:
                # Analyze news sentiment
                sentiment_analysis = analyze_news_sentiment(news_items)
                
                # Display sentiment overview
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Sentiment gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=sentiment_analysis['avg_sentiment'] * 100,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Overall Sentiment Score"},
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
                    sentiment_dist = sentiment_analysis['sentiment_distribution']
                    sentiment_df = pd.DataFrame({
                        'Sentiment': list(sentiment_dist.keys()),
                        'Percentage': list(sentiment_dist.values())
                    })
                    
                    # Sort by sentiment (Positive, Neutral, Negative)
                    sentiment_order = pd.CategoricalDtype(['Positive', 'Neutral', 'Negative'], ordered=True)
                    sentiment_df['Sentiment'] = sentiment_df['Sentiment'].astype(sentiment_order)
                    sentiment_df = sentiment_df.sort_values('Sentiment')
                    
                    fig = px.pie(
                        sentiment_df,
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
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # News items with sentiment
                    st.subheader("Recent News")
                    
                    # Convert news_items to DataFrame for easier filtering
                    news_df = pd.DataFrame(news_items)
                    
                    # Add sentiment filter
                    sentiment_filter = st.multiselect(
                        "Filter by Sentiment",
                        options=["Positive", "Neutral", "Negative"],
                        default=["Positive", "Neutral", "Negative"]
                    )
                    
                    # Filter news
                    filtered_news = news_df[news_df['sentiment'].isin(sentiment_filter)]
                    
                    if not filtered_news.empty:
                        # Display news items
                        for _, item in filtered_news.iterrows():
                            st.markdown(
                                f"<div style='padding:10px; margin-bottom:10px; border-left:3px solid {item['sentiment_color']}; background-color:rgba(0,0,0,0.02);'>"
                                f"<h4 style='margin:0; padding:0;'>{item['title']}</h4>"
                                f"<p style='margin:5px 0; font-size:0.8em; color:gray;'>{item['source']} | {item['date']}</p>"
                                f"<p style='margin:0; color:{item['sentiment_color']};'>Sentiment: {item['sentiment']} ({item['sentiment_score']:.2f})</p>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("No news items match the selected sentiment filter.")
                
                # Sentiment vs. Date chart
                st.subheader("Sentiment Trend")
                
                # Create a DataFrame with date and sentiment
                trend_df = pd.DataFrame({
                    'Date': [datetime.strptime(item['date'], '%Y-%m-%d') for item in news_items],
                    'Sentiment': [item['sentiment_score'] for item in news_items],
                    'Title': [item['title'] for item in news_items]
                })
                
                # Sort by date
                trend_df = trend_df.sort_values('Date')
                
                # Calculate rolling average
                trend_df['Rolling_Sentiment'] = trend_df['Sentiment'].rolling(window=min(3, len(trend_df)), min_periods=1).mean()
                
                # Create the chart
                fig = go.Figure()
                
                # Add individual sentiment points
                fig.add_trace(go.Scatter(
                    x=trend_df['Date'],
                    y=trend_df['Sentiment'],
                    mode='markers',
                    name='News Sentiment',
                    marker=dict(
                        size=10,
                        color=trend_df['Sentiment'],
                        colorscale='RdYlGn',
                        cmin=-1,
                        cmax=1,
                        colorbar=dict(title="Sentiment")
                    ),
                    text=trend_df['Title'],
                    hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Sentiment: %{y:.2f}<extra></extra>'
                ))
                
                # Add rolling average line
                fig.add_trace(go.Scatter(
                    x=trend_df['Date'],
                    y=trend_df['Rolling_Sentiment'],
                    mode='lines',
                    name='Trend',
                    line=dict(color='black', width=2)
                ))
                
                # Add horizontal line at zero
                fig.add_shape(
                    type="line",
                    x0=trend_df['Date'].min(),
                    y0=0,
                    x1=trend_df['Date'].max(),
                    y1=0,
                    line=dict(
                        color="gray",
                        width=1,
                        dash="dash",
                    )
                )
                
                fig.update_layout(
                    title='News Sentiment Trend',
                    xaxis_title='Date',
                    yaxis_title='Sentiment Score',
                    yaxis=dict(range=[-1, 1]),
                    height=350,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No news data available for this stock")
        
        with tab2:
            # Social media sentiment analysis
            st.subheader("Social Media Sentiment")
            
            # Time period selection for social media
            social_period = st.selectbox(
                "Social Media Timeframe",
                ["7 days", "14 days", "30 days"],
                index=0,
                key="social_period"
            )
            
            # Convert period to number of days
            social_days = int(social_period.split()[0])
            
            # Fetch social media sentiment
            with st.spinner("Fetching and analyzing social media sentiment..."):
                social_sentiment = fetch_social_media_sentiment(ticker, days=social_days)
            
            if social_sentiment:
                # Display social media sentiment overview
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Overall sentiment gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=social_sentiment['avg_sentiment'] * 100,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Overall Social Sentiment"},
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
                                'value': social_sentiment['avg_sentiment'] * 100
                            }
                        }
                    ))
                    
                    fig.update_layout(
                        height=250,
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary card
                    sentiment_analyzer = SentimentAnalyzer()
                    sentiment_color = sentiment_analyzer.get_sentiment_color(social_sentiment['avg_sentiment'])
                    
                    st.markdown(
                        f"<div style='padding:15px; border:1px solid #f0f0f0; border-radius:5px;'>"
                        f"<h4 style='margin:0; padding:0; color:{sentiment_color};'>{social_sentiment['overall_sentiment']} Social Sentiment</h4>"
                        f"<p style='margin-top:10px;'>The overall social media sentiment for {ticker} is <span style='color:{sentiment_color};'>{social_sentiment['overall_sentiment'].lower()}</span> based on the analysis of social media discussions over the past {social_days} days.</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                
                with col2:
                    # Sentiment trend chart
                    fig = go.Figure()
                    
                    # Add sentiment line
                    fig.add_trace(go.Scatter(
                        x=social_sentiment['dates'],
                        y=social_sentiment['sentiment_scores'],
                        mode='lines+markers',
                        name='Sentiment',
                        line=dict(color='#1E88E5', width=2),
                        marker=dict(
                            size=8,
                            color=social_sentiment['sentiment_scores'],
                            colorscale='RdYlGn',
                            cmin=-1,
                            cmax=1
                        )
                    ))
                    
                    # Add horizontal line at zero
                    fig.add_shape(
                        type="line",
                        x0=social_sentiment['dates'][0],
                        y0=0,
                        x1=social_sentiment['dates'][-1],
                        y1=0,
                        line=dict(
                            color="gray",
                            width=1,
                            dash="dash",
                        )
                    )
                    
                    fig.update_layout(
                        title='Social Media Sentiment Trend',
                        xaxis_title='Date',
                        yaxis_title='Sentiment Score',
                        yaxis=dict(range=[-1, 1]),
                        height=350,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display volume and sentiment together
                st.subheader("Social Media Volume vs. Sentiment")
                
                # Create figure with secondary y-axis
                fig = go.Figure()
                
                # Add sentiment line
                fig.add_trace(go.Scatter(
                    x=social_sentiment['dates'],
                    y=social_sentiment['sentiment_scores'],
                    mode='lines',
                    name='Sentiment',
                    line=dict(color='#1E88E5', width=2)
                ))
                
                # Add volume bars
                fig.add_trace(go.Bar(
                    x=social_sentiment['dates'],
                    y=social_sentiment['sentiment_volumes'],
                    name='Volume',
                    marker=dict(color='rgba(0, 0, 0, 0.2)'),
                    yaxis='y2'
                ))
                
                # Add horizontal line at zero for sentiment
                fig.add_shape(
                    type="line",
                    x0=social_sentiment['dates'][0],
                    y0=0,
                    x1=social_sentiment['dates'][-1],
                    y1=0,
                    line=dict(
                        color="gray",
                        width=1,
                        dash="dash",
                    )
                )
                
                fig.update_layout(
                    title='Social Media Volume vs. Sentiment',
                    xaxis_title='Date',
                    yaxis_title='Sentiment Score',
                    yaxis2=dict(
                        title='Volume',
                        titlefont=dict(color='rgba(0, 0, 0, 0.5)'),
                        tickfont=dict(color='rgba(0, 0, 0, 0.5)'),
                        overlaying='y',
                        side='right',
                        showgrid=False
                    ),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Social media insights
                st.subheader("Social Media Insights")
                
                # Get some key insights from the data
                recent_sentiment_trend = social_sentiment['sentiment_scores'][-5:]
                recent_trend_direction = np.mean(np.diff(recent_sentiment_trend))
                
                max_sentiment_day = social_sentiment['sentiment_scores'].index(max(social_sentiment['sentiment_scores']))
                min_sentiment_day = social_sentiment['sentiment_scores'].index(min(social_sentiment['sentiment_scores']))
                
                max_volume_day = social_sentiment['sentiment_volumes'].index(max(social_sentiment['sentiment_volumes']))
                
                insights = []
                
                # Trend direction insight
                if recent_trend_direction > 0.05:
                    insights.append({
                        'title': 'Positive Momentum',
                        'description': f'Social sentiment for {ticker} has been increasingly positive over the last few days.',
                        'color': 'green'
                    })
                elif recent_trend_direction < -0.05:
                    insights.append({
                        'title': 'Negative Momentum',
                        'description': f'Social sentiment for {ticker} has been increasingly negative over the last few days.',
                        'color': 'red'
                    })
                
                # Volume insight
                if social_sentiment['sentiment_volumes'][-1] > np.mean(social_sentiment['sentiment_volumes']):
                    insights.append({
                        'title': 'Increased Social Activity',
                        'description': f'Social media discussion volume for {ticker} is currently above average.',
                        'color': 'blue'
                    })
                
                # Sentiment extreme insight
                if max_sentiment_day >= len(social_sentiment['dates']) - 3:
                    insights.append({
                        'title': 'Recent Sentiment Peak',
                        'description': f'Social sentiment for {ticker} recently reached its highest point on {social_sentiment["dates"][max_sentiment_day]}.',
                        'color': 'green'
                    })
                
                if min_sentiment_day >= len(social_sentiment['dates']) - 3:
                    insights.append({
                        'title': 'Recent Sentiment Low',
                        'description': f'Social sentiment for {ticker} recently reached its lowest point on {social_sentiment["dates"][min_sentiment_day]}.',
                        'color': 'red'
                    })
                
                # Display insights
                if insights:
                    for insight in insights:
                        st.markdown(
                            f"<div style='background-color:rgba({{'green': '76, 175, 80', 'red': '244, 67, 54', 'blue': '33, 150, 243'}}['{insight['color']}'], 0.1); padding:10px; border-left:3px solid {{'green': '#4CAF50', 'red': '#F44336', 'blue': '#2196F3'}}['{insight['color']}']; margin-bottom:10px;'>"
                            f"<h4 style='margin:0;'>{insight['title']}</h4>"
                            f"<p>{insight['description']}</p>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No significant social media insights detected for this timeframe.")
            else:
                st.info("No social media sentiment data available for this stock")
        
        with tab3:
            # Combined sentiment analysis and trends
            st.subheader("Sentiment vs. Price Trends")
            
            # Select time period
            combined_period = st.selectbox(
                "Analysis Timeframe",
                ["1mo", "3mo", "6mo", "1y"],
                index=0,
                key="combined_period"
            )
            
            # Fetch stock price data
            stock_data = get_stock_data(ticker, period=combined_period)
            
            # Fetch news for the same period
            days_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
            days_for_news = days_map.get(combined_period, 30)
            
            news_items = fetch_financial_news(ticker, days=days_for_news, max_results=50)
            
            # Fetch social sentiment for the same period
            social_sentiment = fetch_social_media_sentiment(ticker, days=days_for_news)
            
            if stock_data is not None and not stock_data.empty:
                # Prepare news sentiment data by date
                news_sentiment_by_date = {}
                
                if news_items:
                    for item in news_items:
                        date = item['date']
                        if date in news_sentiment_by_date:
                            news_sentiment_by_date[date].append(item['sentiment_score'])
                        else:
                            news_sentiment_by_date[date] = [item['sentiment_score']]
                    
                    # Calculate average sentiment for each date
                    news_sentiment_df = pd.DataFrame(
                        [(date, np.mean(scores)) for date, scores in news_sentiment_by_date.items()],
                        columns=['Date', 'Sentiment']
                    )
                    
                    # Convert to datetime for merging
                    news_sentiment_df['Date'] = pd.to_datetime(news_sentiment_df['Date'])
                    news_sentiment_df = news_sentiment_df.sort_values('Date')
                
                # Create price and sentiment chart
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
                
                # Add news sentiment if available
                if news_items:
                    # Resample to fill missing dates
                    full_date_range = pd.date_range(start=news_sentiment_df['Date'].min(), end=news_sentiment_df['Date'].max())
                    news_sentiment_df = news_sentiment_df.set_index('Date').reindex(full_date_range).fillna(method='ffill').reset_index()
                    news_sentiment_df.columns = ['Date', 'Sentiment']
                    
                    fig.add_trace(go.Scatter(
                        x=news_sentiment_df['Date'],
                        y=news_sentiment_df['Sentiment'],
                        mode='lines',
                        name='News Sentiment',
                        line=dict(color='#4CAF50', width=1.5),
                        yaxis='y2'
                    ))
                
                # Add social sentiment if available
                if social_sentiment:
                    # Convert dates to datetime
                    social_dates = [datetime.strptime(date, '%Y-%m-%d') for date in social_sentiment['dates']]
                    
                    fig.add_trace(go.Scatter(
                        x=social_dates,
                        y=social_sentiment['sentiment_scores'],
                        mode='lines',
                        name='Social Sentiment',
                        line=dict(color='#FF9800', width=1.5, dash='dash'),
                        yaxis='y2'
                    ))
                
                fig.update_layout(
                    title=f"{ticker} Price vs. Sentiment",
                    xaxis_title='Date',
                    yaxis_title='Price (₹)',
                    yaxis2=dict(
                        title='Sentiment Score',
                        titlefont=dict(color='rgba(0, 0, 0, 0.5)'),
                        tickfont=dict(color='rgba(0, 0, 0, 0.5)'),
                        overlaying='y',
                        side='right',
                        range=[-1, 1],
                        showgrid=False
                    ),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    height=500,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Correlation analysis
                st.subheader("Sentiment-Price Correlation Analysis")
                
                # Create correlation table
                correlation_data = []
                
                # News sentiment correlation with price
                if news_items and not news_sentiment_df.empty:
                    # Merge with price data
                    price_df = pd.DataFrame(stock_data['Close'])
                    price_df = price_df.reset_index()
                    price_df.columns = ['Date', 'Price']
                    
                    # Make sure dates are in same format
                    merged_df = pd.merge_asof(
                        news_sentiment_df.sort_values('Date'),
                        price_df.sort_values('Date'),
                        on='Date',
                        direction='nearest'
                    )
                    
                    if len(merged_df) > 5:  # Need enough data for meaningful correlation
                        news_price_corr = merged_df['Sentiment'].corr(merged_df['Price'])
                        correlation_data.append({
                            'Type': 'News Sentiment vs Price',
                            'Correlation': news_price_corr,
                            'Interpretation': interpret_correlation(news_price_corr)
                        })
                        
                        # Calculate lagged correlations (if news sentiment predicts price movements)
                        for lag in [1, 3, 5]:
                            if len(merged_df) > 5 + lag:
                                merged_df[f'Price_Lag_{lag}'] = merged_df['Price'].shift(-lag)
                                lagged_corr = merged_df['Sentiment'].corr(merged_df[f'Price_Lag_{lag}'])
                                correlation_data.append({
                                    'Type': f'News Sentiment vs Price ({lag}-day Lag)',
                                    'Correlation': lagged_corr,
                                    'Interpretation': interpret_correlation(lagged_corr)
                                })
                
                # Social sentiment correlation with price
                if social_sentiment and stock_data is not None:
                    # Convert to DataFrames
                    social_df = pd.DataFrame({
                        'Date': social_dates,
                        'Sentiment': social_sentiment['sentiment_scores']
                    })
                    
                    price_df = pd.DataFrame(stock_data['Close'])
                    price_df = price_df.reset_index()
                    price_df.columns = ['Date', 'Price']
                    
                    # Merge data
                    merged_df = pd.merge_asof(
                        social_df.sort_values('Date'),
                        price_df.sort_values('Date'),
                        on='Date',
                        direction='nearest'
                    )
                    
                    if len(merged_df) > 5:  # Need enough data for meaningful correlation
                        social_price_corr = merged_df['Sentiment'].corr(merged_df['Price'])
                        correlation_data.append({
                            'Type': 'Social Sentiment vs Price',
                            'Correlation': social_price_corr,
                            'Interpretation': interpret_correlation(social_price_corr)
                        })
                        
                        # Calculate lagged correlations (if social sentiment predicts price movements)
                        for lag in [1, 3, 5]:
                            if len(merged_df) > 5 + lag:
                                merged_df[f'Price_Lag_{lag}'] = merged_df['Price'].shift(-lag)
                                lagged_corr = merged_df['Sentiment'].corr(merged_df[f'Price_Lag_{lag}'])
                                correlation_data.append({
                                    'Type': f'Social Sentiment vs Price ({lag}-day Lag)',
                                    'Correlation': lagged_corr,
                                    'Interpretation': interpret_correlation(lagged_corr)
                                })
                
                # Display correlation table
                if correlation_data:
                    corr_df = pd.DataFrame(correlation_data)
                    corr_df['Correlation'] = corr_df['Correlation'].map(lambda x: f"{x:.2f}")
                    
                    st.table(corr_df)
                    
                    st.markdown("""
                    **Interpretation Guide:**
                    * A positive correlation suggests that sentiment and price tend to move in the same direction.
                    * A negative correlation suggests that sentiment and price tend to move in opposite directions.
                    * Lagged correlations show if sentiment tends to lead price movements.
                    * Correlation strength: 0.0-0.3 (weak), 0.3-0.5 (moderate), 0.5-0.7 (strong), 0.7-1.0 (very strong)
                    """)
                else:
                    st.info("Not enough data to calculate meaningful correlations")
            else:
                st.error(f"Unable to fetch price data for ticker: {ticker}")
    else:
        st.error(f"Unable to fetch data for ticker: {ticker}. Please enter a valid ticker symbol.")
    
    # Additional Information
    st.markdown("---")
    st.markdown("""
    ### About Sentiment Analysis
    
    This page analyzes market sentiment for stocks using various sources:
    
    1. **News Sentiment** - Analyzes recent financial news articles and headlines to gauge market sentiment.
    
    2. **Social Media Sentiment** - Examines social media discussions to understand retail investor sentiment.
    
    3. **Sentiment-Price Correlation** - Explores the relationship between sentiment and price movements.
    
    *Note: Sentiment analysis is one of many factors to consider in investment decisions. It should be used alongside fundamental and technical analysis for a comprehensive view.*
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
    else:
        direction = "negative"
    
    return f"{strength} {direction} correlation"
