import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.stock_data import get_stock_data
from utils.pattern_recognition import (
    calculate_technical_indicators,
    identify_candlestick_patterns,
    detect_chart_patterns,
    train_pattern_recognition_model,
    predict_future_movement
)

def show():
    """Display the pattern recognition page"""
    st.header("Pattern Recognition")
    
    # Default ticker and time period
    default_ticker = "AAPL"
    
    # Select stock and time period
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ticker = st.text_input("Enter Ticker Symbol", value=default_ticker).upper()
    
    with col2:
        time_period = st.selectbox(
            "Select Time Period",
            ["3mo", "6mo", "1y", "2y", "5y"],
            index=2  # Default to 1y
        )
    
    # Fetch stock data
    stock_data = get_stock_data(ticker, period=time_period)
    
    if stock_data is not None and not stock_data.empty:
        # Calculate technical indicators
        indicators_data = calculate_technical_indicators(stock_data)
        
        # Identify candlestick patterns
        patterns_data = identify_candlestick_patterns(stock_data)
        
        # Detect chart patterns
        chart_patterns = detect_chart_patterns(stock_data)
        
        # Display candlestick chart with patterns
        st.subheader("Candlestick Chart & Patterns")
        
        # Create tabs for different analysis views
        tab1, tab2, tab3 = st.tabs(["Candlestick Patterns", "Technical Indicators", "ML Prediction"])
        
        with tab1:
            # Create a candlestick chart with pattern markers
            fig = go.Figure()
            
            # Check if data is available
            if patterns_data is not None and not patterns_data.empty:
                # Add candlestick chart
                fig.add_trace(go.Candlestick(
                    x=patterns_data.index,
                    open=patterns_data['Open'],
                    high=patterns_data['High'],
                    low=patterns_data['Low'],
                    close=patterns_data['Close'],
                    name='Price'
                ))
                
                # Add markers for bullish patterns
                bullish_markers = []
                bullish_x = []
                
                for i, row in patterns_data.iterrows():
                    if row.get('BullishEngulfing', False) or row.get('Hammer', False):
                        bullish_markers.append(row['Low'] * 0.99)  # Slightly below the candle
                        bullish_x.append(i)
            else:
                # Add empty trace with a message
                fig.add_annotation(
                    x=0.5, y=0.5,
                    text="No pattern data available",
                    showarrow=False,
                    font=dict(size=20)
                )
            
            if bullish_markers:
                fig.add_trace(go.Scatter(
                    x=bullish_x,
                    y=bullish_markers,
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up',
                        size=10,
                        color='green'
                    ),
                    name='Bullish Pattern'
                ))
            
            # Add markers for bearish patterns
            bearish_markers = []
            bearish_x = []
            
            for i, row in patterns_data.iterrows():
                if row['BearishEngulfing'] or row['ShootingStar']:
                    bearish_markers.append(row['High'] * 1.01)  # Slightly above the candle
                    bearish_x.append(i)
            
            if bearish_markers:
                fig.add_trace(go.Scatter(
                    x=bearish_x,
                    y=bearish_markers,
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=10,
                        color='red'
                    ),
                    name='Bearish Pattern'
                ))
            
            # Add markers for doji
            doji_markers = []
            doji_x = []
            
            for i, row in patterns_data.iterrows():
                if row['Doji']:
                    doji_markers.append(row['High'] * 1.01)  # Slightly above the candle
                    doji_x.append(i)
            
            if doji_markers:
                fig.add_trace(go.Scatter(
                    x=doji_x,
                    y=doji_markers,
                    mode='markers',
                    marker=dict(
                        symbol='circle',
                        size=8,
                        color='blue'
                    ),
                    name='Doji'
                ))
            
            # Add volume as a subplot
            fig.add_trace(go.Bar(
                x=patterns_data.index,
                y=patterns_data['Volume'],
                name='Volume',
                marker=dict(color='rgba(0, 0, 0, 0.2)'),
                yaxis='y2'
            ))
            
            # Add support and resistance levels if available
            if 'support_levels' in chart_patterns and chart_patterns['support_levels']:
                for level in chart_patterns['support_levels'][:3]:  # Show top 3 levels
                    fig.add_shape(
                        type="line",
                        x0=patterns_data.index[0],
                        y0=level,
                        x1=patterns_data.index[-1],
                        y1=level,
                        line=dict(
                            color="green",
                            width=1,
                            dash="dot",
                        )
                    )
            
            if 'resistance_levels' in chart_patterns and chart_patterns['resistance_levels']:
                for level in chart_patterns['resistance_levels'][:3]:  # Show top 3 levels
                    fig.add_shape(
                        type="line",
                        x0=patterns_data.index[0],
                        y0=level,
                        x1=patterns_data.index[-1],
                        y1=level,
                        line=dict(
                            color="red",
                            width=1,
                            dash="dot",
                        )
                    )
            
            fig.update_layout(
                title=f"{ticker} Candlestick Chart with Pattern Recognition",
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
            
            # Display chart pattern insights
            st.subheader("Chart Pattern Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Display trend information
                trend_color = {
                    "Bullish": "green",
                    "Bearish": "red",
                    "Sideways": "gray"
                }.get(chart_patterns.get('trend', 'Sideways'), 'gray')
                
                st.markdown(
                    f"<div style='border:1px solid #f0f0f0; padding:15px; border-radius:5px;'>"
                    f"<h4>Current Trend</h4>"
                    f"<p style='font-size:1.5em; color:{trend_color};'>{chart_patterns.get('trend', 'Unknown')}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
                # Display support/resistance information
                support_levels = chart_patterns.get('support_levels', [])
                resistance_levels = chart_patterns.get('resistance_levels', [])
                
                if support_levels:
                    st.markdown("### Support Levels")
                    for i, level in enumerate(support_levels[:3]):
                        st.markdown(f"{i+1}. ₹{level:.2f}")
                
                if resistance_levels:
                    st.markdown("### Resistance Levels")
                    for i, level in enumerate(resistance_levels[:3]):
                        st.markdown(f"{i+1}. ₹{level:.2f}")
            
            with col2:
                # Display additional pattern information
                golden_cross = chart_patterns.get('golden_cross', False)
                death_cross = chart_patterns.get('death_cross', False)
                
                if golden_cross:
                    st.markdown(
                        "<div style='background-color:rgba(76, 175, 80, 0.1); padding:10px; border-left:3px solid #4CAF50; margin-bottom:10px;'>"
                        "<h4 style='margin:0;'>Golden Cross Detected</h4>"
                        "<p>50-day MA crossed above 200-day MA, a potential bullish signal.</p>"
                        "</div>",
                        unsafe_allow_html=True
                    )
                
                if death_cross:
                    st.markdown(
                        "<div style='background-color:rgba(244, 67, 54, 0.1); padding:10px; border-left:3px solid #F44336; margin-bottom:10px;'>"
                        "<h4 style='margin:0;'>Death Cross Detected</h4>"
                        "<p>50-day MA crossed below 200-day MA, a potential bearish signal.</p>"
                        "</div>",
                        unsafe_allow_html=True
                    )
                
                # Display candlestick pattern information
                st.markdown("### Detected Candlestick Patterns")
                
                # Count patterns in the last 30 days or entire dataset if smaller
                lookback_days = min(30, len(patterns_data))
                recent_data = patterns_data.iloc[-lookback_days:]
                
                bullish_engulfing_count = recent_data['BullishEngulfing'].sum()
                bearish_engulfing_count = recent_data['BearishEngulfing'].sum()
                hammer_count = recent_data['Hammer'].sum()
                shooting_star_count = recent_data['ShootingStar'].sum()
                doji_count = recent_data['Doji'].sum()
                
                pattern_counts = {
                    "Bullish Engulfing": int(bullish_engulfing_count),
                    "Bearish Engulfing": int(bearish_engulfing_count),
                    "Hammer": int(hammer_count),
                    "Shooting Star": int(shooting_star_count),
                    "Doji": int(doji_count)
                }
                
                for pattern, count in pattern_counts.items():
                    if count > 0:
                        st.markdown(f"- {pattern}: {count} instances")
                    
                # If no patterns detected
                if sum(pattern_counts.values()) == 0:
                    st.markdown("No significant candlestick patterns detected in recent data.")
        
        with tab2:
            # Show technical indicator charts
            if indicators_data is not None:
                st.subheader("Technical Indicators")
                
                # Create indicator selection
                indicator_options = [
                    "Moving Averages",
                    "RSI",
                    "MACD",
                    "Bollinger Bands",
                    "Stochastic Oscillator"
                ]
                
                selected_indicators = st.multiselect(
                    "Select Technical Indicators",
                    options=indicator_options,
                    default=["Moving Averages", "RSI"]
                )
                
                # Plot selected indicators
                if "Moving Averages" in selected_indicators:
                    # Moving Averages chart
                    fig = go.Figure()
                    
                    # Add price
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['Close'],
                        mode='lines',
                        name='Close Price',
                        line=dict(color='#1E88E5', width=2)
                    ))
                    
                    # Add moving averages
                    ma_colors = {
                        'MA5': '#FFC107',  # Yellow
                        'MA10': '#FF9800',  # Orange
                        'MA20': '#F44336',  # Red
                        'MA50': '#9C27B0',  # Purple
                        'MA200': '#000000'  # Black
                    }
                    
                    for ma, color in ma_colors.items():
                        if ma in indicators_data.columns:
                            fig.add_trace(go.Scatter(
                                x=indicators_data.index,
                                y=indicators_data[ma],
                                mode='lines',
                                name=ma,
                                line=dict(color=color, width=1)
                            ))
                    
                    fig.update_layout(
                        title='Moving Averages',
                        xaxis_title='Date',
                        yaxis_title='Price (₹)',
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                if "RSI" in selected_indicators:
                    # RSI chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['RSI'],
                        mode='lines',
                        name='RSI',
                        line=dict(color='#2196F3', width=2)
                    ))
                    
                    # Add overbought/oversold lines
                    fig.add_shape(
                        type="line",
                        x0=indicators_data.index[0],
                        y0=70,
                        x1=indicators_data.index[-1],
                        y1=70,
                        line=dict(
                            color="red",
                            width=1,
                            dash="dash",
                        )
                    )
                    
                    fig.add_shape(
                        type="line",
                        x0=indicators_data.index[0],
                        y0=30,
                        x1=indicators_data.index[-1],
                        y1=30,
                        line=dict(
                            color="green",
                            width=1,
                            dash="dash",
                        )
                    )
                    
                    fig.update_layout(
                        title='Relative Strength Index (RSI)',
                        xaxis_title='Date',
                        yaxis_title='RSI',
                        yaxis=dict(range=[0, 100]),
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                if "MACD" in selected_indicators:
                    # MACD chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['MACD'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='#2196F3', width=2)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['MACD_Signal'],
                        mode='lines',
                        name='Signal Line',
                        line=dict(color='#FF9800', width=1)
                    ))
                    
                    # Add histogram
                    colors = ['green' if val >= 0 else 'red' for val in indicators_data['MACD_Hist']]
                    
                    fig.add_trace(go.Bar(
                        x=indicators_data.index,
                        y=indicators_data['MACD_Hist'],
                        name='Histogram',
                        marker_color=colors
                    ))
                    
                    fig.update_layout(
                        title='MACD (Moving Average Convergence Divergence)',
                        xaxis_title='Date',
                        yaxis_title='Value',
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                if "Bollinger Bands" in selected_indicators:
                    # Bollinger Bands chart
                    fig = go.Figure()
                    
                    # Add price
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['Close'],
                        mode='lines',
                        name='Close Price',
                        line=dict(color='#1E88E5', width=2)
                    ))
                    
                    # Add Bollinger Bands
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['BB_Upper'],
                        mode='lines',
                        name='Upper Band',
                        line=dict(color='rgba(244, 67, 54, 0.7)', width=1)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['BB_Middle'],
                        mode='lines',
                        name='Middle Band',
                        line=dict(color='rgba(0, 0, 0, 0.5)', width=1)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['BB_Lower'],
                        mode='lines',
                        name='Lower Band',
                        line=dict(color='rgba(76, 175, 80, 0.7)', width=1),
                        fill='tonexty',
                        fillcolor='rgba(0, 0, 0, 0.05)'
                    ))
                    
                    fig.update_layout(
                        title='Bollinger Bands',
                        xaxis_title='Date',
                        yaxis_title='Price (₹)',
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                if "Stochastic Oscillator" in selected_indicators:
                    # Stochastic Oscillator chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['SlowK'],
                        mode='lines',
                        name='%K',
                        line=dict(color='#2196F3', width=2)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=indicators_data.index,
                        y=indicators_data['SlowD'],
                        mode='lines',
                        name='%D',
                        line=dict(color='#FF9800', width=1)
                    ))
                    
                    # Add overbought/oversold lines
                    fig.add_shape(
                        type="line",
                        x0=indicators_data.index[0],
                        y0=80,
                        x1=indicators_data.index[-1],
                        y1=80,
                        line=dict(
                            color="red",
                            width=1,
                            dash="dash",
                        )
                    )
                    
                    fig.add_shape(
                        type="line",
                        x0=indicators_data.index[0],
                        y0=20,
                        x1=indicators_data.index[-1],
                        y1=20,
                        line=dict(
                            color="green",
                            width=1,
                            dash="dash",
                        )
                    )
                    
                    fig.update_layout(
                        title='Stochastic Oscillator',
                        xaxis_title='Date',
                        yaxis_title='Value',
                        yaxis=dict(range=[0, 100]),
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display key insights based on indicators
                st.subheader("Technical Indicator Insights")
                
                # Current values
                current_rsi = indicators_data['RSI'].iloc[-1] if 'RSI' in indicators_data.columns else None
                current_macd = indicators_data['MACD'].iloc[-1] if 'MACD' in indicators_data.columns else None
                current_signal = indicators_data['MACD_Signal'].iloc[-1] if 'MACD_Signal' in indicators_data.columns else None
                current_price = indicators_data['Close'].iloc[-1]
                current_bb_upper = indicators_data['BB_Upper'].iloc[-1] if 'BB_Upper' in indicators_data.columns else None
                current_bb_lower = indicators_data['BB_Lower'].iloc[-1] if 'BB_Lower' in indicators_data.columns else None
                current_slowk = indicators_data['SlowK'].iloc[-1] if 'SlowK' in indicators_data.columns else None
                current_slowd = indicators_data['SlowD'].iloc[-1] if 'SlowD' in indicators_data.columns else None
                
                # Insights
                insights = []
                
                # RSI insights
                if current_rsi is not None:
                    if current_rsi > 70:
                        insights.append({
                            'indicator': 'RSI',
                            'signal': 'Overbought',
                            'description': f'RSI is at {current_rsi:.2f}, indicating potential overbought conditions.',
                            'color': 'red'
                        })
                    elif current_rsi < 30:
                        insights.append({
                            'indicator': 'RSI',
                            'signal': 'Oversold',
                            'description': f'RSI is at {current_rsi:.2f}, indicating potential oversold conditions.',
                            'color': 'green'
                        })
                
                # MACD insights
                if current_macd is not None and current_signal is not None:
                    if current_macd > current_signal:
                        if indicators_data['MACD'].iloc[-2] <= indicators_data['MACD_Signal'].iloc[-2]:
                            insights.append({
                                'indicator': 'MACD',
                                'signal': 'Bullish Crossover',
                                'description': 'MACD line has crossed above the signal line, potentially indicating upward momentum.',
                                'color': 'green'
                            })
                        else:
                            insights.append({
                                'indicator': 'MACD',
                                'signal': 'Bullish',
                                'description': 'MACD line is above the signal line, potentially indicating upward momentum.',
                                'color': 'green'
                            })
                    elif current_macd < current_signal:
                        if indicators_data['MACD'].iloc[-2] >= indicators_data['MACD_Signal'].iloc[-2]:
                            insights.append({
                                'indicator': 'MACD',
                                'signal': 'Bearish Crossover',
                                'description': 'MACD line has crossed below the signal line, potentially indicating downward momentum.',
                                'color': 'red'
                            })
                        else:
                            insights.append({
                                'indicator': 'MACD',
                                'signal': 'Bearish',
                                'description': 'MACD line is below the signal line, potentially indicating downward momentum.',
                                'color': 'red'
                            })
                
                # Bollinger Bands insights
                if current_bb_upper is not None and current_bb_lower is not None:
                    if current_price >= current_bb_upper:
                        insights.append({
                            'indicator': 'Bollinger Bands',
                            'signal': 'Upper Band Touch',
                            'description': 'Price is at or above the upper Bollinger Band, indicating potential overbought conditions or strong upward momentum.',
                            'color': 'orange'
                        })
                    elif current_price <= current_bb_lower:
                        insights.append({
                            'indicator': 'Bollinger Bands',
                            'signal': 'Lower Band Touch',
                            'description': 'Price is at or below the lower Bollinger Band, indicating potential oversold conditions or strong downward momentum.',
                            'color': 'blue'
                        })
                
                # Stochastic Oscillator insights
                if current_slowk is not None and current_slowd is not None:
                    if current_slowk > 80 and current_slowd > 80:
                        insights.append({
                            'indicator': 'Stochastic',
                            'signal': 'Overbought',
                            'description': 'Stochastic oscillator is in overbought territory, potentially indicating a reversal to the downside.',
                            'color': 'red'
                        })
                    elif current_slowk < 20 and current_slowd < 20:
                        insights.append({
                            'indicator': 'Stochastic',
                            'signal': 'Oversold',
                            'description': 'Stochastic oscillator is in oversold territory, potentially indicating a reversal to the upside.',
                            'color': 'green'
                        })
                    elif current_slowk > current_slowd and indicators_data['SlowK'].iloc[-2] <= indicators_data['SlowD'].iloc[-2]:
                        insights.append({
                            'indicator': 'Stochastic',
                            'signal': 'Bullish Crossover',
                            'description': '%K line has crossed above the %D line, potentially indicating upward momentum.',
                            'color': 'green'
                        })
                    elif current_slowk < current_slowd and indicators_data['SlowK'].iloc[-2] >= indicators_data['SlowD'].iloc[-2]:
                        insights.append({
                            'indicator': 'Stochastic',
                            'signal': 'Bearish Crossover',
                            'description': '%K line has crossed below the %D line, potentially indicating downward momentum.',
                            'color': 'red'
                        })
                
                # Display insights
                if insights:
                    for insight in insights:
                        st.markdown(
                            f"<div style='background-color:rgba({{'green': '76, 175, 80', 'red': '244, 67, 54', 'orange': '255, 152, 0', 'blue': '33, 150, 243'}}['{insight['color']}'], 0.1); padding:10px; border-left:3px solid {{'green': '#4CAF50', 'red': '#F44336', 'orange': '#FF9800', 'blue': '#2196F3'}}['{insight['color']}']; margin-bottom:10px;'>"
                            f"<h4 style='margin:0;'>{insight['indicator']}: {insight['signal']}</h4>"
                            f"<p>{insight['description']}</p>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No significant technical signals detected in the current data.")
            else:
                st.warning("Unable to calculate technical indicators for the selected stock.")
        
        with tab3:
            # Machine Learning Prediction
            st.subheader("ML-Based Pattern Recognition")
            
            if indicators_data is not None:
                # Train the model
                feature_cols = [
                    'MA5', 'MA10', 'MA20', 'MA50', 'RSI', 'MACD', 'MACD_Signal', 
                    'MACD_Hist', 'BB_Upper', 'BB_Middle', 'BB_Lower', 'SlowK', 'SlowD',
                    'OBV', 'Volume_ROC', 'ROC', 'Williams_%R'
                ]
                
                # Make sure all required features are present
                for feature in feature_cols:
                    if feature not in indicators_data.columns:
                        st.warning(f"Missing feature: {feature}. Cannot perform ML prediction.")
                        break
                else:
                    # All features are present, continue with training
                    with st.spinner("Training pattern recognition model..."):
                        model, scaler = train_pattern_recognition_model(indicators_data)
                        
                        if model is not None and scaler is not None:
                            # Make prediction
                            prediction_prob = predict_future_movement(model, scaler, indicators_data, feature_cols)
                            
                            # Display prediction
                            st.subheader("Price Movement Prediction")
                            
                            # Create a gauge chart for prediction probability
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=prediction_prob * 100,
                                title={'text': "Probability of Upward Movement"},
                                gauge={
                                    'axis': {'range': [0, 100]},
                                    'bar': {'color': "darkblue"},
                                    'steps': [
                                        {'range': [0, 30], 'color': "red"},
                                        {'range': [30, 70], 'color': "gray"},
                                        {'range': [70, 100], 'color': "green"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "black", 'width': 4},
                                        'thickness': 0.75,
                                        'value': prediction_prob * 100
                                    }
                                }
                            ))
                            
                            fig.update_layout(
                                height=300,
                                margin=dict(l=20, r=20, t=50, b=20)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Prediction interpretation
                            if prediction_prob > 0.7:
                                prediction_text = "Strong Bullish Signal"
                                prediction_color = "green"
                                prediction_description = "The model predicts a high probability of upward price movement in the near future."
                            elif prediction_prob > 0.55:
                                prediction_text = "Moderate Bullish Signal"
                                prediction_color = "lightgreen"
                                prediction_description = "The model predicts a moderate probability of upward price movement in the near future."
                            elif prediction_prob < 0.3:
                                prediction_text = "Strong Bearish Signal"
                                prediction_color = "red"
                                prediction_description = "The model predicts a high probability of downward price movement in the near future."
                            elif prediction_prob < 0.45:
                                prediction_text = "Moderate Bearish Signal"
                                prediction_color = "lightcoral"
                                prediction_description = "The model predicts a moderate probability of downward price movement in the near future."
                            else:
                                prediction_text = "Neutral Signal"
                                prediction_color = "gray"
                                prediction_description = "The model does not predict a strong directional movement in the near future."
                            
                            st.markdown(
                                f"<div style='background-color:rgba({{'green': '76, 175, 80', 'lightgreen': '129, 199, 132', 'red': '244, 67, 54', 'lightcoral': '239, 154, 154', 'gray': '158, 158, 158'}}['{prediction_color}'], 0.1); padding:15px; border-left:3px solid {{'green': '#4CAF50', 'lightgreen': '#81C784', 'red': '#F44336', 'lightcoral': '#EF9A9A', 'gray': '#9E9E9E'}}['{prediction_color}']'>"
                                f"<h3 style='margin:0; color:{{'green': '#2E7D32', 'lightgreen': '#388E3C', 'red': '#C62828', 'lightcoral': '#D32F2F', 'gray': '#616161'}}['{prediction_color}'];'>{prediction_text}</h3>"
                                f"<p style='margin-top:10px;'>{prediction_description}</p>"
                                f"<p style='margin-top:10px;'><b>Prediction score:</b> {prediction_prob:.2f} (on a scale of 0 to 1)</p>"
                                f"<p style='font-size:0.8em; color:gray; margin-top:10px;'>Note: This prediction is based on historical patterns and technical indicators. It should not be considered as financial advice.</p>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                            # Show most important features
                            if hasattr(model, 'feature_importances_'):
                                st.subheader("Feature Importance")
                                
                                # Get feature importances
                                importances = model.feature_importances_
                                indices = np.argsort(importances)[::-1]
                                
                                # Create a DataFrame for display
                                importance_df = pd.DataFrame({
                                    'Feature': [feature_cols[i] for i in indices],
                                    'Importance': [importances[i] for i in indices]
                                })
                                
                                # Plot feature importances
                                fig = px.bar(
                                    importance_df.head(10),  # Top 10 features
                                    x='Importance',
                                    y='Feature',
                                    orientation='h',
                                    title='Top 10 Most Important Technical Indicators'
                                )
                                
                                fig.update_layout(
                                    yaxis_title='',
                                    xaxis_title='Relative Importance',
                                    height=350,
                                    margin=dict(l=0, r=0, t=30, b=0)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Unable to train prediction model. Not enough data or too many missing values.")
            else:
                st.warning("Unable to calculate technical indicators for the selected stock.")
    else:
        st.error(f"Unable to fetch data for ticker: {ticker}. Please enter a valid ticker symbol.")
    
    # Additional Information
    st.markdown("---")
    st.markdown("""
    ### About Pattern Recognition
    
    This page analyzes stock price patterns using various technical analysis methods:
    
    1. **Candlestick Patterns** - Identifies patterns like Doji, Hammer, Shooting Star, and Engulfing patterns that may signal potential reversals or continuation of trends.
    
    2. **Technical Indicators** - Calculates and visualizes indicators like Moving Averages, RSI, MACD, Bollinger Bands, and Stochastic Oscillator to help identify market conditions.
    
    3. **Support & Resistance** - Detects key price levels where the stock has historically reversed direction.
    
    4. **ML Prediction** - Uses machine learning to identify patterns in historical data and predict potential future price movements.
    
    *Note: These patterns and predictions are based solely on historical price action and should not be considered as financial advice. Always conduct thorough research and consider multiple factors when making investment decisions.*
    """)
