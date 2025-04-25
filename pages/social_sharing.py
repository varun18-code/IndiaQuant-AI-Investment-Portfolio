import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from io import BytesIO
import re
import time

from utils.portfolio import load_portfolio
from utils.social_sharing import (
    generate_text_summary,
    generate_performance_image,
    generate_allocation_image,
    generate_shareable_portfolio_card,
    get_share_links,
    generate_qr_code,
    get_image_download_link,
    send_sms_update
)

def show():
    """Display the social sharing page"""
    st.title("Share Your Portfolio")
    
    st.markdown("""
    Share your portfolio insights with friends, family, or financial advisors!
    Generate a customized summary of your portfolio's performance and share it via various platforms.
    """)
    
    # Load the user's portfolio
    portfolio = load_portfolio()
    portfolio_value = portfolio.get_portfolio_value()
    performance_metrics = portfolio.calculate_portfolio_metrics()
    
    if portfolio_value['positions']:
        with st.container():
            st.subheader("Portfolio Summary")
            
            total_value = portfolio_value['total_value']
            
            # Display portfolio summary
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.metric(
                    "Total Value",
                    f"₹{total_value:,.2f}", 
                    f"{portfolio_value['total_gain_loss_pct']:.2f}%"
                )
                
            with col2:
                # Performance info
                if performance_metrics:
                    st.metric(
                        "Annual Return",
                        f"{performance_metrics.get('annualized_return', 0):.2f}%",
                        None
                    )
                
            with col3:
                # Sharpe ratio
                if performance_metrics:
                    st.metric(
                        "Sharpe Ratio",
                        f"{performance_metrics.get('sharpe_ratio', 0):.2f}",
                        None
                    )
            
            st.markdown("---")
            
            # Create sharing option tabs
            tab1, tab2, tab3 = st.tabs(["Text Summary", "Portfolio Card", "QR Code"])
            
            with tab1:
                st.subheader("Text Summary")
                
                # Generate a text summary for sharing
                text_summary = generate_text_summary(portfolio_value, performance_metrics)
                
                # Show the summary in a text area that can be copied
                st.text_area("Portfolio Summary Text", text_summary, height=200)
                
                # Show sharing options for text
                st.subheader("Share Via:")
                
                # Get sharing links
                share_links = get_share_links(text_summary, title="My IndiaQuant Portfolio")
                
                # Create a row of sharing buttons
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"[![WhatsApp](https://img.icons8.com/color/48/000000/whatsapp.png)]({share_links['whatsapp']})")
                    st.markdown("WhatsApp", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"[![Email](https://img.icons8.com/color/48/000000/gmail.png)]({share_links['email']})")
                    st.markdown("Email", unsafe_allow_html=True)
                    
                with col3:
                    st.markdown(f"[![Twitter](https://img.icons8.com/color/48/000000/twitter.png)]({share_links['twitter']})")
                    st.markdown("Twitter", unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"[![Telegram](https://img.icons8.com/color/48/000000/telegram-app.png)]({share_links['telegram']})")
                    st.markdown("Telegram", unsafe_allow_html=True)
                
                # SMS sharing option
                st.markdown("---")
                st.subheader("Share via SMS")
                
                with st.expander("Send via SMS"):
                    # Show a form for sending SMS
                    with st.form(key="sms_form"):
                        phone_input = st.text_input(
                            "Enter phone number (include country code, e.g., +91XXXXXXXXXX)",
                            placeholder="+91XXXXXXXXXX"
                        )
                        
                        # Validate phone format
                        phone_valid = bool(re.match(r'^\+\d{1,3}\d{10}$', phone_input)) if phone_input else False
                        
                        if not phone_valid and phone_input:
                            st.warning("Please enter a valid phone number with country code (e.g., +91XXXXXXXXXX)")
                        
                        # SMS submission button
                        submit_sms = st.form_submit_button("Send SMS")
                        
                        if submit_sms:
                            if not phone_valid:
                                st.error("Invalid phone number format. Please use the international format with country code.")
                            else:
                                # Check if Twilio credentials are configured
                                with st.spinner("Sending SMS..."):
                                    response = send_sms_update(phone_input, text_summary)
                                    
                                    if response['success']:
                                        st.success(response['message'])
                                    else:
                                        st.error(response['message'])
                                        
                                        # If it's a credentials issue, show instructions
                                        if "credentials not configured" in response['message']:
                                            st.info("""
                                            To use SMS sharing, Twilio credentials need to be configured.
                                            Please set the following environment variables:
                                            - TWILIO_ACCOUNT_SID
                                            - TWILIO_AUTH_TOKEN
                                            - TWILIO_PHONE_NUMBER
                                            """)
            
            with tab2:
                st.subheader("Portfolio Card")
                
                # Generate portfolio returns data for the performance image
                portfolio_returns = portfolio.get_portfolio_returns()
                
                # Create a shareable portfolio card
                with st.spinner("Generating portfolio card..."):
                    image_data = generate_shareable_portfolio_card(portfolio_value, performance_metrics)
                
                if image_data:
                    # Display the image
                    st.image(image_data, use_column_width=True)
                    
                    # Provide download link
                    st.markdown(
                        get_image_download_link(image_data, "portfolio_card.png", "Download Portfolio Card"),
                        unsafe_allow_html=True
                    )
                    
                    # Social sharing options for the image
                    st.subheader("Share Image Via:")
                    
                    # Since direct image sharing via links is limited, provide instructions
                    st.info("""
                    To share this image:
                    1. Download the image using the link above
                    2. Attach it to your preferred messaging app or email
                    """)
                    
                    # Add a copy button for convenience
                    if st.button("Copy Portfolio Summary to Clipboard"):
                        # Generate text and use a safer method for clipboard
                        text_for_sharing = generate_text_summary(portfolio_value, performance_metrics)
                        # Create a text area with the content that can be easily copied
                        st.text_area("Portfolio Summary (Select all and copy)", text_for_sharing, height=150)
                        st.success("Select the text above and press Ctrl+C to copy!")
                else:
                    st.error("Failed to generate portfolio card. Please try again.")
            
            with tab3:
                st.subheader("QR Code")
                st.markdown("""
                Generate a QR code with your portfolio summary that can be scanned by others.
                This is ideal for quickly sharing with someone in person.
                """)
                
                # Generate a text summary for the QR code
                qr_text = generate_text_summary(portfolio_value, performance_metrics)
                
                # Create the QR code
                with st.spinner("Generating QR code..."):
                    qr_image = generate_qr_code(qr_text)
                
                if qr_image:
                    # Display the QR code
                    st.image(qr_image, width=300)
                    
                    # Provide download link
                    st.markdown(
                        get_image_download_link(qr_image, "portfolio_qr.png", "Download QR Code"),
                        unsafe_allow_html=True
                    )
                    
                    st.info("""
                    When someone scans this QR code, they'll be able to read your portfolio summary.
                    Print this QR code or display it on your device for others to scan.
                    """)
                else:
                    st.error("Failed to generate QR code. Please try again.")
    else:
        # No portfolio data
        st.warning("""
        Your portfolio is empty. Add some positions in the Portfolio Management page first.
        
        Once you have positions in your portfolio, you'll be able to share your portfolio insights.
        """)
        
        # Add a demo button to show examples
        if st.button("Show Example"):
            st.subheader("Example Portfolio Summary")
            
            example_text = """
            My Portfolio Summary (via IndiaQuant):
            Total Value: ₹456,789.00
            Overall Return: 12.54%
            Annual Return: 8.76%
            Sharpe Ratio: 1.25

            Generated on 28-03-2025
            """
            
            st.text_area("Example Text Summary", example_text, height=200)
            
            # Generate a sample image instead of using external placeholder
            import numpy as np
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a sample portfolio card
            width, height = 800, 400
            image = Image.new('RGB', (width, height), color=(240, 242, 246))
            draw = ImageDraw.Draw(image)
            
            # Add title
            draw.rectangle([(0, 0), (width, 60)], fill=(66, 114, 202))
            draw.text((width//2, 30), "Example Portfolio Card", fill=(255, 255, 255), anchor="mm")
            
            # Add some sample data
            draw.text((width//2, 100), "Portfolio Allocation", fill=(60, 60, 60), anchor="mm")
            
            # Sample bars representing allocation
            colors = [(25, 118, 210), (56, 142, 60), (211, 47, 47), (123, 31, 162)]
            positions = [("RELIANCE", 35), ("INFY", 25), ("HDFC", 20), ("TCS", 20)]
            
            bar_y = 150
            bar_height = 40
            for i, (stock, pct) in enumerate(positions):
                bar_width = int((width - 100) * (pct / 100))
                draw.rectangle([(50, bar_y), (50 + bar_width, bar_y + bar_height)], fill=colors[i])
                if bar_width > 80:
                    draw.text((50 + bar_width//2, bar_y + bar_height//2), f"{stock}: {pct}%", fill=(255, 255, 255), anchor="mm")
                bar_y += 50
            
            # Footer
            draw.rectangle([(0, height-40), (width, height)], fill=(240, 242, 246))
            draw.text((width//2, height-20), "Generated by IndiaQuant", fill=(100, 100, 100), anchor="mm")
            
            st.image(image)
            
            st.info("These are example visualizations. Add positions to your portfolio to create your own.")
    
    # Additional information
    st.markdown("---")
    st.markdown("""
    ### About Portfolio Sharing
    
    Sharing your portfolio information can help you:
    
    - Get feedback from financial advisors or experienced investors
    - Track and communicate your investment progress with family members
    - Document your investment journey for personal reference
    - Create accountability partners for your financial goals
    
    **Privacy Notice**: Your portfolio data is not stored on our servers. All sharing options generate data locally in your browser.
    SMS sharing requires providing a phone number, which is used only for message delivery.
    """)