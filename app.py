import streamlit as st
import datetime
from pages import (
    dashboard, stock_analysis, pattern_recognition, sentiment_analysis, 
    alternative_data, portfolio_management, futures_options, social_sharing,
    financial_advisor, financial_mood_ring, voice_assistant
)

# Configure page settings
st.set_page_config(
    page_title="IndiaQuant: AI-Powered Indian Market Portfolio Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        background: linear-gradient(90deg, #FF6B6B, #4472CA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.2rem;
        color: #4B5563;
        margin-top: 0;
        margin-bottom: 20px;
    }
    
    /* Navigation styling */
    .nav-section {
        margin-bottom: 20px;
    }
    
    /* Card styling */
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid #4472CA;
    }
    
    /* Glossary styling */
    .glossary-term {
        font-weight: bold;
        color: #4472CA;
    }
    
    .glossary-definition {
        font-size: 0.9rem;
        color: #4B5563;
    }
    
    /* Market status indicator */
    .market-open {
        color: #10B981;
        font-weight: bold;
    }
    
    .market-closed {
        color: #EF4444;
        font-weight: bold;
    }

    /* Tooltip for financial terms */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #4472CA;
        cursor: help;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 300px;
        background-color: #f8f9fa;
        color: #333;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        border: 1px solid #ddd;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -150px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.85rem;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# App title and subtitle with enhanced styling
st.markdown('<h1 class="main-title">IndiaQuant: AI-Powered Indian Market Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Advanced portfolio analytics and insights for NSE and BSE investors</p>', unsafe_allow_html=True)

# Financial terms dictionary
financial_terms = {
    "Alpha": "Excess return of an investment relative to the return of a benchmark index",
    "Beta": "Measure of a stock's volatility in relation to the overall market",
    "Sharpe Ratio": "Measure of risk-adjusted return that indicates excess return per unit of risk",
    "Sortino Ratio": "Similar to Sharpe ratio but only considers downside risk",
    "Volatility": "Statistical measure of the dispersion of returns for a security or market index",
    "Max Drawdown": "Maximum observed loss from a peak to a trough of a portfolio before a new peak is attained",
    "NSE": "National Stock Exchange of India - India's leading stock exchange",
    "BSE": "Bombay Stock Exchange - Asia's oldest stock exchange located in Mumbai",
    "NIFTY 50": "Benchmark Indian stock market index representing 50 largest companies listed on NSE",
    "SENSEX": "Benchmark index of BSE composed of 30 of the largest and most actively traded stocks",
    "FII": "Foreign Institutional Investors who invest in Indian financial markets",
    "DII": "Domestic Institutional Investors like mutual funds and insurance companies",
    "F&O": "Futures and Options - derivative financial instruments",
    "SIP": "Systematic Investment Plan - method of investing regularly in mutual funds",
    "NAV": "Net Asset Value - value of a mutual fund's assets minus liabilities, divided by total units",
    "Dividend Yield": "Annual dividend amount per share divided by the current stock price",
    "P/E Ratio": "Price-to-Earnings ratio - valuation metric showing current price relative to earnings",
    "Market Cap": "Total market value of a company's outstanding shares",
    "Volume": "Number of shares or contracts traded during a specified period",
    "Support Level": "Price level where a downtrend can be expected to pause due to buying interest",
    "Resistance Level": "Price level where an uptrend can be expected to pause due to selling interest",
    "MACD": "Moving Average Convergence Divergence - trend-following momentum indicator",
    "RSI": "Relative Strength Index - momentum oscillator measuring speed and change of price movements",
    "Bollinger Bands": "Volatility bands placed above and below a moving average",
    "Moving Average": "Technical indicator showing average price over a specific time period",
    "Bull Market": "Market condition where prices are rising or expected to rise",
    "Bear Market": "Market condition where prices are falling or expected to fall"
}

# Sidebar navigation with enhanced UI
st.sidebar.markdown('<div class="nav-section"><h2>📊 Navigation</h2></div>', unsafe_allow_html=True)

# Navigation with icons
page_icons = {
    "Dashboard": "🏠",
    "Portfolio Management": "💼",
    "Stock Analysis": "📈",
    "Pattern Recognition": "🔍",
    "Sentiment Analysis": "📊",
    "Alternative Data": "📡",
    "Futures & Options": "🔮",
    "Financial Advisor": "🤖",
    "Financial Mood Ring": "💍",
    "Voice Assistant": "🎤",
    "Share Portfolio": "🔗"
}

page_descriptions = {
    "Dashboard": "Overview of your portfolio and market trends",
    "Portfolio Management": "Add, manage, and analyze your stock and mutual fund investments",
    "Stock Analysis": "In-depth technical and fundamental analysis of Indian stocks",
    "Pattern Recognition": "Identify chart patterns and trading signals using AI",
    "Sentiment Analysis": "Market sentiment based on news and social media analysis",
    "Alternative Data": "Insights from non-traditional data sources",
    "Futures & Options": "Analysis and forecasting of futures and options contracts",
    "Financial Advisor": "AI chatbot for personalized financial advice and budget optimization",
    "Financial Mood Ring": "Track your emotional investment state and improve decision-making",
    "Voice Assistant": "Voice-activated financial assistant with regional language support",
    "Share Portfolio": "Share your portfolio insights via social media, SMS, or QR code"
}

page = st.sidebar.radio(
    "Select a page",
    list(page_icons.keys()),
    format_func=lambda x: f"{page_icons[x]} {x}"
)

# Show page description
st.sidebar.markdown(f"<div style='margin-bottom:20px; font-size:0.9rem;'>{page_descriptions[page]}</div>", unsafe_allow_html=True)

# Check if market is open (simplified logic based on IST)
now = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)  # Convert to IST
is_weekday = now.weekday() < 5  # Monday-Friday
is_market_hours = 9 <= now.hour <= 15 and not (now.hour == 9 and now.minute < 15) and not (now.hour == 15 and now.minute > 30)
market_status = "Open" if (is_weekday and is_market_hours) else "Closed"
market_status_class = "market-open" if market_status == "Open" else "market-closed"

# Show market status
st.sidebar.markdown(f"""
<div class="card">
    <h3>Market Status</h3>
    <p>NSE/BSE: <span class="{market_status_class}">{market_status}</span></p>
    <p>Trading Hours: 9:15 AM - 3:30 PM IST (Mon-Fri)</p>
    <p>Current Time (IST): {now.strftime('%H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

# Display the selected page
if page == "Dashboard":
    dashboard.show()
elif page == "Portfolio Management":
    portfolio_management.show()
elif page == "Stock Analysis":
    stock_analysis.show()
elif page == "Pattern Recognition":
    pattern_recognition.show()
elif page == "Sentiment Analysis":
    sentiment_analysis.show()
elif page == "Alternative Data":
    alternative_data.show()
elif page == "Futures & Options":
    futures_options.show()
elif page == "Financial Advisor":
    financial_advisor.show()
elif page == "Financial Mood Ring":
    financial_mood_ring.show()
elif page == "Voice Assistant":
    voice_assistant.show()
elif page == "Share Portfolio":
    social_sharing.show()

# Financial Glossary section in the sidebar
with st.sidebar.expander("📘 Financial Terms Glossary"):
    st.markdown("<h4>Key Financial Terms</h4>", unsafe_allow_html=True)
    
    # Search box for terms
    search_term = st.text_input("Search for a term", "")
    
    # Display filtered terms or all if no search
    filtered_terms = {k: v for k, v in financial_terms.items() 
                     if search_term.lower() in k.lower() or search_term.lower() in v.lower()}
    
    if filtered_terms:
        for term, definition in filtered_terms.items():
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <span class="glossary-term">{term}</span>
                <div class="glossary-definition">{definition}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No matching terms found.")

# Footer with enhanced styling
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align:center;">
    <p>© 2025 IndiaQuant</p>
    <p style="font-size:0.8rem; color:#6B7280;">Advanced analytics for Indian markets</p>
</div>
""", unsafe_allow_html=True)

# Add info about key features in the footer
st.sidebar.markdown("""
<div style="font-size:0.8rem; color:#6B7280; margin-top:20px;">
    <p>Features:</p>
    <ul style="padding-left:15px;">
        <li>Real-time NSE/BSE data</li>
        <li>AI pattern recognition</li>
        <li>Sentiment analysis</li>
        <li>Mutual fund tracking</li>
        <li>Advanced portfolio metrics</li>
        <li>Personalized AI financial advice</li>
        <li>Interactive budget optimizer</li>
        <li>Emotional investment tracking</li>
        <li>Voice assistant with regional language support</li>
        <li>Social sharing capabilities</li>
        <li>Satellite imagery analysis</li>
    </ul>
</div>
""", unsafe_allow_html=True)
