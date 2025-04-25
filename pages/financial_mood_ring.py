"""
Financial Mood Ring module for tracking user emotional investment state
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
from datetime import datetime, timedelta
import random
import json
import os
from PIL import Image
from io import BytesIO
import base64
import colorsys

def show():
    """Display the financial mood ring page"""
    
    st.title("Financial Mood Ring")
    
    # Introduction
    st.markdown("""
    ### Understand Your Investor Psychology
    
    This interactive tool helps you track your emotional state while making investment decisions.
    Research shows that emotional biases often lead to poor financial choices. By becoming aware
    of your emotional patterns, you can make more rational decisions and improve your returns.
    
    **How it works:**
    1. Record your mood before making investment decisions
    2. Track your emotional patterns over time 
    3. See correlations between your emotions and market movements
    4. Receive personalized insights to improve your investment psychology
    """)
    
    # Initialize session state for mood tracking
    if 'mood_history' not in st.session_state:
        st.session_state.mood_history = []
    
    if 'last_mood_date' not in st.session_state:
        st.session_state.last_mood_date = None
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Mood Check-in", "Mood History", "Emotional Analysis", "Investor Psychology Tips"])
    
    with tab1:
        mood_check_in()
    
    with tab2:
        show_mood_history()
    
    with tab3:
        emotional_analysis()
    
    with tab4:
        show_psychology_tips()

def mood_check_in():
    """Allow user to check in their current mood"""
    
    st.header("Today's Mood Check-in")
    
    # Check if user already recorded mood today
    today = datetime.now().date()
    
    if st.session_state.last_mood_date == today:
        st.info("You've already recorded your mood today. You can update it below.")
    
    # Create columns for a better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Market sentiment
        st.subheader("Your Market Sentiment")
        market_sentiment = st.slider(
            "How do you feel about the market today?",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = Extremely Bearish, 10 = Extremely Bullish"
        )
        
        # Confidence level
        st.subheader("Your Confidence Level")
        confidence = st.slider(
            "How confident are you in your investment decisions today?",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = Very Uncertain, 10 = Very Confident"
        )
        
        # Anxiety level
        st.subheader("Your Anxiety Level")
        anxiety = st.slider(
            "How anxious do you feel about your investments today?",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = Very Calm, 10 = Very Anxious"
        )
        
        # FOMO (Fear of Missing Out)
        st.subheader("Your FOMO Level")
        fomo = st.slider(
            "How much FOMO (Fear of Missing Out) are you experiencing?",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = No FOMO, 10 = Extreme FOMO"
        )
        
        # Recent news impact
        st.subheader("News Impact on Your Mood")
        news_impact = st.slider(
            "How much is recent financial news affecting your mood?",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = Not at all, 10 = Significantly"
        )
    
    with col2:
        # Create a mood ring visualization based on inputs
        st.subheader("Your Mood Ring")
        
        # Calculate the mood metrics
        risk_appetite = (market_sentiment + confidence - anxiety) / 3
        emotional_bias = (anxiety + fomo + news_impact) / 3
        
        # Create mood ring visualization
        mood_ring_html = generate_mood_ring(risk_appetite, emotional_bias)
        st.markdown(mood_ring_html, unsafe_allow_html=True)
        
        # Determine the investor type
        investor_type = determine_investor_type(market_sentiment, confidence, anxiety, fomo, news_impact)
        st.markdown(f"**Current Investor Type:** {investor_type}")
    
    # Notes about today's mood
    st.subheader("Investment Notes")
    notes = st.text_area("What factors are influencing your investment mood today?", 
                         placeholder="Examples: Earnings reports, Economic data, Personal financial situation, etc.")
    
    # Investment actions
    st.subheader("Planned Actions")
    actions = st.multiselect(
        "What investment actions are you planning to take today?",
        ["Buy stocks/funds", "Sell stocks/funds", "Rebalance portfolio", 
         "Research only", "Wait and observe", "Deposit more funds", "Withdraw funds"]
    )
    
    # Save mood data
    if st.button("Save Today's Mood"):
        # Create mood data entry
        mood_data = {
            "date": today.strftime("%Y-%m-%d"),
            "market_sentiment": market_sentiment,
            "confidence": confidence,
            "anxiety": anxiety,
            "fomo": fomo,
            "news_impact": news_impact,
            "risk_appetite": risk_appetite,
            "emotional_bias": emotional_bias,
            "investor_type": investor_type,
            "notes": notes,
            "actions": actions
        }
        
        # Update session state
        # If already logged today, update the entry
        if st.session_state.last_mood_date == today:
            for i, entry in enumerate(st.session_state.mood_history):
                if entry["date"] == today.strftime("%Y-%m-%d"):
                    st.session_state.mood_history[i] = mood_data
                    break
        else:
            st.session_state.mood_history.append(mood_data)
            st.session_state.last_mood_date = today
        
        st.success("Your mood has been recorded! Check the Mood History tab to see your emotional patterns.")

def generate_mood_ring(risk_appetite, emotional_bias):
    """Generate a visual mood ring based on risk appetite and emotional bias"""
    
    # Map risk appetite (1-10) to hue (0-240)
    # Higher risk appetite = warmer colors (reds, oranges)
    # Lower risk appetite = cooler colors (blues, greens)
    hue = max(0, min(240 - (risk_appetite * 24), 240))
    
    # Map emotional bias (1-10) to brightness
    # Higher emotional bias = brighter
    brightness = 0.5 + (emotional_bias / 20)
    
    # Convert HSV to RGB
    rgb = colorsys.hsv_to_rgb(hue/360, 0.8, brightness)
    
    # Convert RGB to hex
    color = "#{:02x}{:02x}{:02x}".format(
        int(rgb[0] * 255), 
        int(rgb[1] * 255), 
        int(rgb[2] * 255)
    )
    
    # Create CSS for mood ring
    ring_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; margin: 20px 0;">
        <div style="width: 120px; height: 120px; border-radius: 60px; 
                   background: radial-gradient(circle at 30% 30%, white, {color});
                   box-shadow: 0 0 15px rgba(0,0,0,0.2), inset 0 0 8px rgba(0,0,0,0.1);
                   border: 1px solid #ccc;">
        </div>
        <div style="margin-top: 15px; text-align: center;">
            <div style="font-weight: bold; margin-bottom: 5px;">Mood Metrics</div>
            <div style="font-size: 0.9rem;">Risk Appetite: {risk_appetite:.1f}/10</div>
            <div style="font-size: 0.9rem;">Emotional Bias: {emotional_bias:.1f}/10</div>
        </div>
    </div>
    """
    
    return ring_html

def determine_investor_type(sentiment, confidence, anxiety, fomo, news_impact):
    """Determine the investor type based on mood metrics"""
    
    risk_appetite = (sentiment + confidence - anxiety) / 3
    emotional_bias = (anxiety + fomo + news_impact) / 3
    
    if risk_appetite >= 7 and emotional_bias <= 4:
        return "Calculated Risk-Taker"
    elif risk_appetite >= 7 and emotional_bias > 4:
        return "Emotional Optimist"
    elif risk_appetite >= 4 and risk_appetite < 7 and emotional_bias <= 4:
        return "Balanced Investor"
    elif risk_appetite >= 4 and risk_appetite < 7 and emotional_bias > 4:
        return "News-Reactive Investor"
    elif risk_appetite < 4 and emotional_bias <= 4:
        return "Conservative Planner"
    else:  # risk_appetite < 4 and emotional_bias > 4
        return "Anxious Guardian"

def show_mood_history():
    """Display the user's mood history"""
    
    st.header("Your Mood History")
    
    if not st.session_state.mood_history:
        st.info("You haven't recorded any moods yet. Go to the Mood Check-in tab to get started.")
        # For demo, add sample data
        if st.button("Add Sample Data for Demonstration"):
            add_sample_mood_data()
            st.rerun()
    else:
        # Create a DataFrame for visualization
        df = pd.DataFrame(st.session_state.mood_history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Display mood history as a line chart
        st.subheader("Mood Metrics Over Time")
        
        # Create a multi-line chart for mood metrics
        fig = px.line(
            df, 
            x='date', 
            y=['market_sentiment', 'confidence', 'anxiety', 'fomo', 'news_impact', 'risk_appetite', 'emotional_bias'],
            title="Your Emotional Investment Journey",
            labels={'value': 'Score (1-10)', 'date': 'Date', 'variable': 'Metric'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Investor Type Transitions
        st.subheader("Your Investor Type Transitions")
        
        # Create a timeline of investor types
        fig = go.Figure()
        
        investor_types = df['investor_type'].unique()
        color_map = {
            "Calculated Risk-Taker": "#1E88E5",
            "Emotional Optimist": "#FFC107",
            "Balanced Investor": "#4CAF50",
            "News-Reactive Investor": "#FF9800",
            "Conservative Planner": "#9C27B0",
            "Anxious Guardian": "#F44336"
        }
        
        for i, row in df.iterrows():
            investor_type = row['investor_type']
            fig.add_trace(go.Scatter(
                x=[row['date'], row['date']],
                y=[0, 1],
                mode='lines',
                line=dict(color=color_map.get(investor_type, "#666"), width=20),
                name=investor_type,
                showlegend=investor_type not in fig.data,
                hoverinfo='text',
                hovertext=f"Date: {row['date'].strftime('%Y-%m-%d')}<br>Investor Type: {investor_type}"
            ))
        
        fig.update_layout(
            height=200,
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            margin=dict(l=20, r=20, t=30, b=20),
            hovermode="closest",
            title="Your Investor Type Timeline"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display individual entries
        st.subheader("Detailed Mood Entries")
        
        for i, entry in enumerate(reversed(st.session_state.mood_history)):
            with st.expander(f"Entry from {entry['date']}", expanded=True if i == 0 else False):
                # Create 2 columns
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Market Sentiment:** {entry['market_sentiment']}/10")
                    st.markdown(f"**Confidence Level:** {entry['confidence']}/10")
                    st.markdown(f"**Anxiety Level:** {entry['anxiety']}/10")
                    st.markdown(f"**FOMO Level:** {entry['fomo']}/10")
                    st.markdown(f"**News Impact:** {entry['news_impact']}/10")
                    
                    if entry.get('notes'):
                        st.markdown("**Notes:**")
                        st.markdown(f"*{entry['notes']}*")
                    
                    if entry.get('actions'):
                        st.markdown("**Planned Actions:**")
                        for action in entry['actions']:
                            st.markdown(f"- {action}")
                
                with col2:
                    # Display mood ring for this entry
                    mood_ring_html = generate_mood_ring(entry['risk_appetite'], entry['emotional_bias'])
                    st.markdown(mood_ring_html, unsafe_allow_html=True)
                    st.markdown(f"**Investor Type:** {entry['investor_type']}")

def emotional_analysis():
    """Analyze the user's emotional patterns"""
    
    st.header("Your Emotional Investment Analysis")
    
    if not st.session_state.mood_history or len(st.session_state.mood_history) < 3:
        st.info("You need at least 3 mood entries for meaningful analysis. Go to the Mood Check-in tab to add more entries.")
        return
    
    # Create a DataFrame for analysis
    df = pd.DataFrame(st.session_state.mood_history)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Calculate emotional volatility
    emotional_volatility = df[['market_sentiment', 'confidence', 'anxiety', 'fomo', 'news_impact']].std().mean()
    
    # Create radar chart of average mood metrics
    avg_metrics = df[['market_sentiment', 'confidence', 'anxiety', 'fomo', 'news_impact']].mean().reset_index()
    avg_metrics.columns = ['metric', 'value']
    
    fig = px.line_polar(
        avg_metrics, 
        r='value', 
        theta='metric', 
        line_close=True,
        range_r=[0, 10],
        title="Your Emotional Investment Profile"
    )
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Investor type distribution
    st.subheader("Your Investor Type Distribution")
    
    type_counts = df['investor_type'].value_counts().reset_index()
    type_counts.columns = ['investor_type', 'count']
    
    fig = px.pie(
        type_counts,
        values='count',
        names='investor_type',
        title="Your Investor Type Distribution",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(margin=dict(t=40, b=40, l=40, r=40))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Emotional tendencies
    st.subheader("Your Emotional Investment Tendencies")
    
    # Create columns for different insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Emotional Volatility", f"{emotional_volatility:.2f}/10", 
                  delta_color="inverse",
                  delta="Low" if emotional_volatility < 2 else ("Moderate" if emotional_volatility < 4 else "High"))
        
        most_common_type = type_counts.iloc[0]['investor_type']
        st.metric("Primary Investor Type", most_common_type)
        
        avg_risk = df['risk_appetite'].mean()
        st.metric("Average Risk Appetite", f"{avg_risk:.1f}/10",
                 delta=f"{'Conservative' if avg_risk < 4 else ('Balanced' if avg_risk < 7 else 'Aggressive')}")
    
    with col2:
        avg_emotional_bias = df['emotional_bias'].mean()
        st.metric("Average Emotional Bias", f"{avg_emotional_bias:.1f}/10",
                 delta=f"{'Low' if avg_emotional_bias < 4 else ('Moderate' if avg_emotional_bias < 7 else 'High')}",
                 delta_color="inverse")
        
        most_volatile = df[['market_sentiment', 'confidence', 'anxiety', 'fomo', 'news_impact']].std().idxmax()
        st.metric("Most Volatile Metric", most_volatile.replace("_", " ").title())
        
        emotion_correlation = df[['anxiety', 'fomo', 'news_impact']].mean().sum() / 30
        st.metric("Emotion-Driven Score", f"{emotion_correlation:.2f}",
                 delta=f"{'Low' if emotion_correlation < 0.4 else ('Moderate' if emotion_correlation < 0.7 else 'High')}",
                 delta_color="inverse")
    
    # Personalized insights
    st.subheader("Your Personalized Insights")
    
    insights = generate_personalized_insights(df)
    
    for i, insight in enumerate(insights):
        st.markdown(f"""
        <div style="background-color: rgba(240, 242, 246, 0.8); 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin-bottom: 10px;
                    border-left: 4px solid #2575fc;">
            <p style="margin: 0;"><strong>Insight {i+1}:</strong> {insight}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Behavioral recommendations
    st.subheader("Your Personalized Recommendations")
    
    recommendations = generate_behavioral_recommendations(df)
    
    for i, rec in enumerate(recommendations):
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="background-color: #2575fc; 
                        color: white; 
                        width: 25px; 
                        height: 25px; 
                        border-radius: 50%; 
                        text-align: center; 
                        line-height: 25px;
                        margin-right: 10px;
                        flex-shrink: 0;">
                {i+1}
            </div>
            <div style="background-color: rgba(240, 242, 246, 0.8); 
                        padding: 10px 15px; 
                        border-radius: 8px;
                        flex-grow: 1;">
                {rec}
            </div>
        </div>
        """, unsafe_allow_html=True)

def generate_personalized_insights(df):
    """Generate personalized insights based on mood history"""
    
    insights = []
    
    # Insight 1: Emotional volatility
    emotional_volatility = df[['market_sentiment', 'confidence', 'anxiety', 'fomo', 'news_impact']].std().mean()
    if emotional_volatility < 2:
        insights.append("Your emotional state is very stable, which is excellent for long-term investing. This stability can help you stick to your investment plan even during market volatility.")
    elif emotional_volatility < 4:
        insights.append("You have a moderately stable emotional profile. While you experience natural fluctuations in sentiment, you generally maintain consistent emotional patterns.")
    else:
        insights.append("Your emotional state shows significant volatility. This could lead to reactive investment decisions. Consider implementing structured decision-making processes to balance these emotional swings.")
    
    # Insight 2: Most common investor type
    most_common_type = df['investor_type'].value_counts().idxmax()
    type_descriptions = {
        "Calculated Risk-Taker": "You're comfortable taking calculated risks while keeping emotions in check. This balanced approach can lead to strong long-term results when paired with thorough analysis.",
        "Emotional Optimist": "Your optimism drives you to seek opportunities, but your emotional biases may sometimes cloud judgment. Implementing systematic checks before major decisions could be beneficial.",
        "Balanced Investor": "You maintain a healthy balance between risk and caution, while keeping emotions relatively controlled. This balanced approach serves most investors well over time.",
        "News-Reactive Investor": "You're significantly influenced by market news and may react quickly to headlines. Developing a more systematic approach to evaluating news could improve decision quality.",
        "Conservative Planner": "You take a cautious approach while maintaining emotional discipline. While this protects capital, ensure you're not being too conservative for your long-term goals.",
        "Anxious Guardian": "Your caution is driven by emotional concerns about market risks. This protective stance helps avoid losses but may limit growth potential."
    }
    insights.append(f"You primarily exhibit traits of a {most_common_type}. {type_descriptions.get(most_common_type, '')}")
    
    # Insight 3: FOMO analysis
    avg_fomo = df['fomo'].mean()
    if avg_fomo > 6:
        insights.append("Your FOMO (Fear Of Missing Out) levels are consistently high. This might drive you to chase hot investments after they've already peaked. Developing a FOMO-resistance strategy is important for your long-term returns.")
    
    # Insight 4: News impact
    avg_news_impact = df['news_impact'].mean()
    if avg_news_impact > 6:
        insights.append("Financial news strongly influences your emotional state. While staying informed is important, remember that financial media often amplifies short-term movements. Consider limiting news consumption to scheduled times.")
    
    # Insight 5: Risk appetite vs. emotional bias correlation
    correlation = df[['risk_appetite', 'emotional_bias']].corr().iloc[0,1]
    if correlation > 0.5:
        insights.append("Your risk appetite increases with your emotional bias, suggesting you may take more risks when emotionally charged. This pattern can lead to buying high and selling low. Consider implementing cooling-off periods before major decisions.")
    elif correlation < -0.5:
        insights.append("You tend to become more cautious when emotionally charged, which may cause you to miss opportunities during market excitement. Having pre-set investment criteria can help maintain appropriate risk-taking during emotional periods.")
    
    return insights

def generate_behavioral_recommendations(df):
    """Generate behavioral recommendations based on mood patterns"""
    
    recommendations = []
    
    # Calculate key metrics
    emotional_volatility = df[['market_sentiment', 'confidence', 'anxiety', 'fomo', 'news_impact']].std().mean()
    avg_anxiety = df['anxiety'].mean()
    avg_fomo = df['fomo'].mean()
    avg_news_impact = df['news_impact'].mean()
    
    # Recommendation based on emotional volatility
    if emotional_volatility > 3:
        recommendations.append("Implement a mandatory 24-hour reflection period before making any investment decision when your emotional metrics change by more than 3 points in any category.")
    
    # Recommendation based on anxiety
    if avg_anxiety > 6:
        recommendations.append("Create a 'worry journal' where you document specific investment concerns, their likelihood, and potential impact. Review this journal periodically to identify patterns in your anxieties and how often they actually materialize.")
    
    # Recommendation based on FOMO
    if avg_fomo > 6:
        recommendations.append("Before investing in 'hot' opportunities, write down specifically what evidence (not emotion) supports the investment and what specific metrics would indicate it's time to sell.")
    
    # Recommendation based on news impact
    if avg_news_impact > 6:
        recommendations.append("Limit financial news consumption to scheduled times (e.g., 30 minutes in the morning and evening) rather than continuous monitoring. This reduces emotional reactivity to headlines.")
    
    # General recommendations
    recommendations.append("Record both your emotional state and the specific investment decisions you make in response. Review this log quarterly to identify which emotional states led to your best and worst decisions.")
    
    recommendations.append("Create a personal investment policy statement that clearly outlines your investment goals, time horizon, risk tolerance, and specific criteria for investment decisions. Review this when emotions are running high.")
    
    # Recommendation based on most common investor type
    most_common_type = df['investor_type'].value_counts().idxmax()
    
    type_recommendations = {
        "Calculated Risk-Taker": "Balance your comfort with risk by implementing structured position sizing rules. Limit any single position to a predefined percentage of your portfolio regardless of conviction level.",
        "Emotional Optimist": "Create a pre-investment checklist that includes contrarian questions: 'What could go wrong?' and 'What evidence contradicts my thesis?' Answer these in writing before investing.",
        "Balanced Investor": "Maintain your balanced approach while implementing a systematic rebalancing schedule (e.g., quarterly) to ensure your portfolio doesn't drift toward either excessive risk or excessive caution.",
        "News-Reactive Investor": "For each major piece of financial news, write down its likely impact on your investments over different time frames: 1 week, 1 month, 1 year, and 5 years. This helps distinguish between short-term noise and long-term significance.",
        "Conservative Planner": "Review your long-term financial goals annually to ensure your conservative approach isn't creating a gap between your investment returns and your required future capital.",
        "Anxious Guardian": "Allocate a small percentage of your portfolio (5-10%) as an 'opportunity fund' that allows for calculated risk-taking without endangering your core financial security."
    }
    
    if most_common_type in type_recommendations:
        recommendations.append(type_recommendations[most_common_type])
    
    return recommendations

def show_psychology_tips():
    """Display investor psychology tips"""
    
    st.header("Investor Psychology Tips")
    
    st.markdown("""
    Understanding the psychological aspects of investing can significantly improve your decision-making.
    Here are key cognitive biases that affect investors and strategies to overcome them.
    """)
    
    # Create expandable sections for each cognitive bias
    with st.expander("Loss Aversion", expanded=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style="background-color: #ffebee; padding: 10px; border-radius: 5px;">
                <h4 style="color: #c62828; margin-top: 0;">The Bias</h4>
                <p>The pain of losses is psychologically about twice as powerful as the pleasure of gains.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px;">
                <h4 style="color: #2e7d32; margin-top: 0;">Overcoming Strategies</h4>
                <ul>
                    <li>Focus on total portfolio performance rather than individual positions</li>
                    <li>Establish predetermined exit strategies before investing</li>
                    <li>Reframe losses as the cost of education and long-term growth</li>
                    <li>Set regular portfolio review schedules rather than checking constantly</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("Recency Bias"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style="background-color: #ffebee; padding: 10px; border-radius: 5px;">
                <h4 style="color: #c62828; margin-top: 0;">The Bias</h4>
                <p>Overweighting recent events and experiences when making decisions, assuming patterns from the immediate past will continue.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px;">
                <h4 style="color: #2e7d32; margin-top: 0;">Overcoming Strategies</h4>
                <ul>
                    <li>Study longer historical periods when analyzing investments</li>
                    <li>Maintain a decision journal to track your thinking at different market phases</li>
                    <li>Ask: "Would I make this same decision if the market had been flat the past month?"</li>
                    <li>Consider multiple future scenarios, not just extensions of the present</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("Confirmation Bias"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style="background-color: #ffebee; padding: 10px; border-radius: 5px;">
                <h4 style="color: #c62828; margin-top: 0;">The Bias</h4>
                <p>Seeking information that confirms existing beliefs while avoiding contradictory data.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px;">
                <h4 style="color: #2e7d32; margin-top: 0;">Overcoming Strategies</h4>
                <ul>
                    <li>Actively seek contradictory information to your investment thesis</li>
                    <li>Follow analysts and sources with different viewpoints</li>
                    <li>Ask a trusted friend to play "devil's advocate" on major investment decisions</li>
                    <li>Create a pre-investment checklist that includes examining contrary evidence</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("Herd Mentality"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style="background-color: #ffebee; padding: 10px; border-radius: 5px;">
                <h4 style="color: #c62828; margin-top: 0;">The Bias</h4>
                <p>Following what others are doing based on emotional contagion rather than independent analysis.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px;">
                <h4 style="color: #2e7d32; margin-top: 0;">Overcoming Strategies</h4>
                <ul>
                    <li>Develop your own investment philosophy and written criteria</li>
                    <li>Limit exposure to investment social media during volatile markets</li>
                    <li>Wait 24-48 hours before acting on "hot tips" or trending investments</li>
                    <li>Calculate and record your own valuation rather than relying on market consensus</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("Anchoring Bias"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style="background-color: #ffebee; padding: 10px; border-radius: 5px;">
                <h4 style="color: #c62828; margin-top: 0;">The Bias</h4>
                <p>Over-relying on the first piece of information encountered (like purchase price) when making decisions.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px;">
                <h4 style="color: #2e7d32; margin-top: 0;">Overcoming Strategies</h4>
                <ul>
                    <li>Regularly reevaluate investments as if you were seeing them for the first time</li>
                    <li>Use the "blind analysis" technique - evaluate metrics without knowing which company they belong to</li>
                    <li>Ask "Would I buy this investment today at the current price?" If no, consider selling</li>
                    <li>Set price targets based on intrinsic value calculations, not purchase price</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("Overconfidence Bias"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style="background-color: #ffebee; padding: 10px; border-radius: 5px;">
                <h4 style="color: #c62828; margin-top: 0;">The Bias</h4>
                <p>Overestimating knowledge, abilities, and the precision of information, leading to excessive risk-taking.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px;">
                <h4 style="color: #2e7d32; margin-top: 0;">Overcoming Strategies</h4>
                <ul>
                    <li>Track your predictions and review their accuracy periodically</li>
                    <li>Use probability ranges rather than point estimates in your analysis</li>
                    <li>Implement position sizing rules that limit exposure to any single investment</li>
                    <li>Seek feedback from others, especially those with different perspectives</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Research-backed best practices section
    st.subheader("Research-Backed Best Practices")
    
    best_practices = [
        {
            "title": "Decision Journaling",
            "description": "Keep a record of investment decisions, including your rationale, emotional state, and expected outcomes. Review periodically to identify patterns in your decision-making.",
            "research": "Studies show that reflective practice improves decision-making over time by making cognitive biases more visible and identifiable to practitioners."
        },
        {
            "title": "Systematic Rebalancing",
            "description": "Set a regular schedule (e.g., quarterly) to rebalance your portfolio back to target allocations, regardless of market sentiment.",
            "research": "Research suggests that systematic rebalancing can add approximately 0.5% in annual returns while reducing portfolio volatility."
        },
        {
            "title": "Implementation Intentions",
            "description": "Create specific 'if-then' plans for various market scenarios before they occur (e.g., 'If investment X drops 20%, then I will reevaluate but not immediately sell').",
            "research": "Psychological research shows that pre-commitment to specific responses in anticipated situations significantly improves decision quality under emotional stress."
        },
        {
            "title": "Cooling-Off Periods",
            "description": "Implement mandatory waiting periods (24-48 hours) before making significant investment decisions, especially during market extremes.",
            "research": "Studies demonstrate that even short cooling-off periods can significantly reduce the impact of emotional reactions on financial decisions."
        }
    ]
    
    for practice in best_practices:
        st.markdown(f"""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <h4 style="color: #1565c0; margin-top: 0;">{practice['title']}</h4>
            <p><strong>Practice:</strong> {practice['description']}</p>
            <p><strong>Research:</strong> <em>{practice['research']}</em></p>
        </div>
        """, unsafe_allow_html=True)

def add_sample_mood_data():
    """Add sample mood data for demonstration"""
    
    # Generate sample data for the last 14 days
    sample_data = []
    
    today = datetime.now().date()
    
    # Create sample patterns
    for i in range(14):
        entry_date = today - timedelta(days=14-i)
        
        # Create a realistic pattern (market dip and recovery)
        if i < 3:
            # Normal market
            sentiment = random.randint(5, 7)
            confidence = random.randint(6, 8)
            anxiety = random.randint(3, 5)
            fomo = random.randint(4, 6)
            news_impact = random.randint(3, 5)
        elif i < 6:
            # Market starts declining
            sentiment = random.randint(3, 5)
            confidence = random.randint(4, 6)
            anxiety = random.randint(5, 7)
            fomo = random.randint(3, 5)
            news_impact = random.randint(6, 8)
        elif i < 9:
            # Market bottom
            sentiment = random.randint(2, 4)
            confidence = random.randint(3, 5)
            anxiety = random.randint(7, 9)
            fomo = random.randint(2, 4)
            news_impact = random.randint(7, 9)
        elif i < 12:
            # Recovery begins
            sentiment = random.randint(5, 7)
            confidence = random.randint(5, 7)
            anxiety = random.randint(5, 7)
            fomo = random.randint(5, 7)
            news_impact = random.randint(5, 7)
        else:
            # Bull market
            sentiment = random.randint(7, 9)
            confidence = random.randint(7, 9)
            anxiety = random.randint(2, 4)
            fomo = random.randint(6, 8)
            news_impact = random.randint(4, 6)
        
        # Calculate metrics
        risk_appetite = (sentiment + confidence - anxiety) / 3
        emotional_bias = (anxiety + fomo + news_impact) / 3
        
        # Determine investor type
        investor_type = determine_investor_type(sentiment, confidence, anxiety, fomo, news_impact)
        
        # Create notes based on the phase
        if i < 3:
            notes = "Market seems stable. Considering adding to positions gradually."
        elif i < 6:
            notes = "Concerned about recent economic data. Market looks uncertain."
        elif i < 9:
            notes = "Significant market decline. Worried about portfolio losses."
        elif i < 12:
            notes = "Signs of recovery appearing. Still cautious but more optimistic."
        else:
            notes = "Strong market recovery. Looking for growth opportunities."
        
        # Create actions based on the phase
        if i < 3:
            actions = ["Research only", "Buy stocks/funds"]
        elif i < 6:
            actions = ["Wait and observe", "Research only"]
        elif i < 9:
            actions = ["Wait and observe"]
        elif i < 12:
            actions = ["Research only", "Rebalance portfolio"]
        else:
            actions = ["Buy stocks/funds", "Deposit more funds"]
        
        # Create the entry
        entry = {
            "date": entry_date.strftime("%Y-%m-%d"),
            "market_sentiment": sentiment,
            "confidence": confidence,
            "anxiety": anxiety,
            "fomo": fomo,
            "news_impact": news_impact,
            "risk_appetite": risk_appetite,
            "emotional_bias": emotional_bias,
            "investor_type": investor_type,
            "notes": notes,
            "actions": actions
        }
        
        sample_data.append(entry)
    
    # Add to session state
    st.session_state.mood_history = sample_data
    st.session_state.last_mood_date = None  # Allow new entry today

# Run the show function when this module is executed
if __name__ == "__main__":
    show()