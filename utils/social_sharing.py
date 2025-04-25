import streamlit as st
import base64
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont

def generate_text_summary(portfolio_value, performance_metrics):
    """
    Generate a text summary of portfolio performance for sharing
    
    Parameters:
    portfolio_value (dict): Portfolio value information
    performance_metrics (dict): Performance metrics
    
    Returns:
    str: Formatted text summary
    """
    total_value = portfolio_value.get('total_value', 0)
    total_gain_loss_pct = portfolio_value.get('total_gain_loss_pct', 0)
    
    # Get performance metrics if available
    total_return = performance_metrics.get('total_return', 0) if performance_metrics else 0
    sharpe_ratio = performance_metrics.get('sharpe_ratio', 0) if performance_metrics else 0
    
    # Generate summary text
    summary = f"My Portfolio Summary (via IndiaQuant):\n"
    summary += f"Total Value: ₹{total_value:,.2f}\n"
    summary += f"Overall Return: {total_gain_loss_pct:.2f}%\n"
    
    if performance_metrics:
        summary += f"Annual Return: {performance_metrics.get('annualized_return', 0):.2f}%\n"
        summary += f"Sharpe Ratio: {sharpe_ratio:.2f}\n"
    
    summary += f"\nGenerated on {datetime.now().strftime('%d-%m-%Y')}"
    
    return summary

def generate_performance_image(portfolio_returns, benchmark_returns=None, title="My Portfolio Performance"):
    """
    Generate a shareable image of portfolio performance
    
    Parameters:
    portfolio_returns (pd.DataFrame): DataFrame with portfolio returns
    benchmark_returns (pd.Series): Series with benchmark returns
    title (str): Chart title
    
    Returns:
    BytesIO: Image in memory buffer or None if generation fails
    """
    try:
        # Create a placeholder image with text instead of plotly chart
        # since we can't rely on kaleido being available
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Add a blue header
        draw_allocation_box(draw, 0, 0, width, 60, (30, 136, 229))
        
        # Try to load fonts
        try:
            title_font = ImageFont.truetype("Arial Bold.ttf", 24)
            subtitle_font = ImageFont.truetype("Arial.ttf", 18)
            body_font = ImageFont.truetype("Arial.ttf", 14)
        except IOError:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        # Add title
        draw.text((width//2, 30), title, fill=(255, 255, 255), font=title_font, anchor="mm")
        
        # Add some portfolio stats
        if portfolio_returns is not None and not portfolio_returns.empty:
            try:
                latest_return = portfolio_returns['Portfolio_Cumulative_Return'].iloc[-1] * 100
                
                # Calculate some statistics
                max_return = portfolio_returns['Portfolio_Cumulative_Return'].max() * 100
                min_return = portfolio_returns['Portfolio_Cumulative_Return'].min() * 100
                
                # Add the stats to the image
                draw.text((width//2, 100), f"Portfolio Performance", 
                         fill=(30, 136, 229), font=subtitle_font, anchor="mm")
                
                draw.text((width//2, 140), f"Current Return: {latest_return:.2f}%", 
                         fill=(0, 0, 0), font=body_font, anchor="mm")
                
                draw.text((width//2, 180), f"Highest Return: {max_return:.2f}%", 
                         fill=(0, 0, 0), font=body_font, anchor="mm")
                
                draw.text((width//2, 220), f"Lowest Return: {min_return:.2f}%", 
                         fill=(0, 0, 0), font=body_font, anchor="mm")
                
                # Add benchmark comparison if available
                if benchmark_returns is not None and not benchmark_returns.empty:
                    benchmark_latest = ((1 + benchmark_returns).cumprod() - 1).iloc[-1] * 100
                    draw.text((width//2, 260), f"Benchmark Return: {benchmark_latest:.2f}%", 
                             fill=(0, 0, 0), font=body_font, anchor="mm")
                    
                    diff = latest_return - benchmark_latest
                    color = (0, 128, 0) if diff >= 0 else (255, 0, 0)
                    draw.text((width//2, 300), f"Difference: {diff:+.2f}%", 
                             fill=color, font=body_font, anchor="mm")
            except Exception as e:
                draw.text((width//2, 180), "Error calculating statistics", 
                         fill=(255, 0, 0), font=body_font, anchor="mm")
        else:
            draw.text((width//2, 180), "No performance data available", 
                     fill=(0, 0, 0), font=body_font, anchor="mm")
        
        # Add footer
        draw_allocation_box(draw, 0, height-40, width, height, (245, 245, 245))
        draw.text((width//2, height-20), "Powered by IndiaQuant", 
                 fill=(100, 100, 100), font=body_font, anchor="mm")
        
        # Save to in-memory buffer
        img_bytes = BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    except Exception as e:
        st.error(f"Failed to generate performance image: {e}")
        return None

def draw_allocation_box(draw, x0, y0, x1, y1, color):
    """Helper function to draw rectangular boxes correctly"""
    draw.rectangle(((x0, y0), (x1, y1)), fill=color)

def generate_allocation_image(portfolio_value, title="My Portfolio Allocation"):
    """
    Generate a shareable image of portfolio allocation
    
    Parameters:
    portfolio_value (dict): Portfolio value information
    title (str): Chart title
    
    Returns:
    BytesIO: Image in memory buffer or None if generation fails
    """
    try:
        positions = portfolio_value.get('positions', [])
        
        if not positions:
            # Create an empty placeholder
            width, height = 800, 400
            image = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype("Arial.ttf", 18)
            except IOError:
                font = ImageFont.load_default()
            
            draw.text((width//2, height//2), "No allocation data available", 
                     fill=(100, 100, 100), font=font, anchor="mm")
            
            img_bytes = BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes
        
        # Create a simple representation of allocation with PIL
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Add a header
        draw_allocation_box(draw, 0, 0, width, 60, (30, 136, 229))
        
        # Try to load fonts
        try:
            title_font = ImageFont.truetype("Arial Bold.ttf", 24)
            subtitle_font = ImageFont.truetype("Arial.ttf", 18)
            regular_font = ImageFont.truetype("Arial.ttf", 14)
        except IOError:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            regular_font = ImageFont.load_default()
        
        # Add title
        draw.text((width//2, 30), title, fill=(255, 255, 255), font=title_font, anchor="mm")
        
        # Calculate total value
        total_value = sum([p['current_value'] for p in positions])
        
        # Sort positions by value
        positions_sorted = sorted(positions, key=lambda p: p['current_value'], reverse=True)
        
        # Draw a simple "pie chart" as colored rectangles with labels
        max_positions = min(len(positions), 10)  # Limit to 10 positions for readability
        
        # Colors for the allocation bars
        colors = [
            (25, 118, 210),   # Blue
            (56, 142, 60),    # Green
            (211, 47, 47),    # Red
            (123, 31, 162),   # Purple
            (255, 143, 0),    # Orange
            (0, 151, 167),    # Teal
            (191, 54, 12),    # Deep Orange
            (46, 125, 50),    # Dark Green
            (106, 27, 154),   # Deep Purple
            (2, 119, 189),    # Light Blue
        ]
        
        # Draw legend
        legend_y_start = 100
        legend_spacing = 40
        
        for i, pos in enumerate(positions_sorted[:max_positions]):
            if i < len(colors):
                color = colors[i]
            else:
                # Generate a random color if we run out
                color = (np.random.randint(0, 200), np.random.randint(0, 200), np.random.randint(0, 200))
            
            # Calculate percentage
            percentage = (pos['current_value'] / total_value) * 100
            
            # Draw color box
            draw_allocation_box(draw, 50, legend_y_start + i*legend_spacing, 
                               80, legend_y_start + i*legend_spacing + 20, color)
            
            # Draw ticker and percentage
            ticker_text = pos['ticker'].replace(".NS", "").replace(".BO", "")
            draw.text((100, legend_y_start + i*legend_spacing + 10), 
                     f"{ticker_text} - ₹{pos['current_value']:,.2f} ({percentage:.1f}%)", 
                     fill=(0, 0, 0), font=regular_font, anchor="lm")
        
        # Draw a horizontal bar chart
        bar_start_y = 180 + max_positions * legend_spacing
        bar_height = 30
        bar_spacing = 10
        bar_width = width - 100
        
        draw.text((width//2, bar_start_y - 30), "Portfolio Allocation", 
                 fill=(30, 136, 229), font=subtitle_font, anchor="mm")
        
        # Draw the bars
        current_x = 50
        for i, pos in enumerate(positions_sorted[:max_positions]):
            if i < len(colors):
                color = colors[i]
            else:
                color = (np.random.randint(0, 200), np.random.randint(0, 200), np.random.randint(0, 200))
            
            # Calculate width based on percentage
            percentage = (pos['current_value'] / total_value)
            pos_width = int(bar_width * percentage)
            
            # Draw the bar
            draw_allocation_box(draw, current_x, bar_start_y,
                               current_x + pos_width, bar_start_y + bar_height, color)
            
            current_x += pos_width
        
        # Add percentages on a separate line for readability
        current_x = 50
        for i, pos in enumerate(positions_sorted[:max_positions]):
            percentage = (pos['current_value'] / total_value)
            pos_width = int(bar_width * percentage)
            
            # Only add text if the segment is wide enough
            if pos_width > 40:
                # Draw the ticker in the middle of its segment
                ticker_text = pos['ticker'].replace(".NS", "").replace(".BO", "")
                draw.text((current_x + pos_width//2, bar_start_y + bar_height + 15), 
                        f"{ticker_text}", fill=(0, 0, 0), font=regular_font, anchor="mm")
                
                # Draw the percentage below
                draw.text((current_x + pos_width//2, bar_start_y + bar_height + 35), 
                        f"{percentage*100:.1f}%", fill=(0, 0, 0), font=regular_font, anchor="mm")
            
            current_x += pos_width
        
        # Add additional information
        info_y = bar_start_y + bar_height + 80
        
        draw.text((width//2, info_y), f"Total Portfolio Value: ₹{total_value:,.2f}", 
                 fill=(0, 0, 0), font=subtitle_font, anchor="mm")
        
        draw.text((width//2, info_y + 40), f"Total Holdings: {len(positions)}", 
                 fill=(0, 0, 0), font=regular_font, anchor="mm")
        
        # Add footer
        draw_allocation_box(draw, 0, height-40, width, height, (245, 245, 245))
        draw.text((width//2, height-20), "Powered by IndiaQuant", 
                 fill=(100, 100, 100), font=regular_font, anchor="mm")
        
        # Save to in-memory buffer
        img_bytes = BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    except Exception as e:
        st.error(f"Failed to generate allocation image: {e}")
        return None

def generate_shareable_portfolio_card(portfolio_value, performance_metrics=None):
    """
    Generate a beautiful, shareable portfolio summary card image
    
    Parameters:
    portfolio_value (dict): Portfolio value information
    performance_metrics (dict): Performance metrics
    
    Returns:
    BytesIO: Image in memory buffer
    """
    # Create a blank image
    width, height = 1200, 630  # Standard social sharing size
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Add gradient background
    for y in range(height):
        r = int(24 + (y / height) * 30)
        g = int(140 + (y / height) * 30)
        b = int(229 - (y / height) * 30)
        for x in range(width):
            draw.point((x, y), fill=(r, g, b))
    
    # Add semi-transparent white overlay for content area
    overlay = Image.new('RGBA', (width-100, height-100), (255, 255, 255, 230))
    image.paste(overlay, (50, 50), overlay)
    
    # Try to load a font, or use default
    try:
        title_font = ImageFont.truetype("Arial Bold.ttf", 48)
        subtitle_font = ImageFont.truetype("Arial.ttf", 36)
        regular_font = ImageFont.truetype("Arial.ttf", 28)
        small_font = ImageFont.truetype("Arial.ttf", 24)
    except IOError:
        # Use default font if custom font fails
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Add title
    draw.text((width//2, 100), "My Investment Portfolio", 
              fill=(255, 255, 255), font=title_font, anchor="mm")
    
    # Add portfolio summary
    total_value = portfolio_value.get('total_value', 0)
    total_gain_loss = portfolio_value.get('total_gain_loss', 0)
    total_gain_loss_pct = portfolio_value.get('total_gain_loss_pct', 0)
    
    # Center aligned values
    draw.text((width//2, 180), f"Total Value: ₹{total_value:,.2f}", 
              fill=(20, 20, 20), font=subtitle_font, anchor="mm")
    
    # Determine color based on gain/loss
    gain_color = (46, 125, 50) if total_gain_loss > 0 else (198, 40, 40)
    gain_symbol = "↑" if total_gain_loss > 0 else "↓"
    
    draw.text((width//2, 240), f"Total Gain/Loss: ₹{total_gain_loss:,.2f} ({total_gain_loss_pct:.2f}% {gain_symbol})", 
              fill=gain_color, font=regular_font, anchor="mm")
    
    # Add performance metrics if available
    if performance_metrics:
        metrics_y = 320
        metrics = [
            ("Annual Return", f"{performance_metrics.get('annualized_return', 0):.2f}%"),
            ("Sharpe Ratio", f"{performance_metrics.get('sharpe_ratio', 0):.2f}"),
            ("Max Drawdown", f"{performance_metrics.get('max_drawdown', 0):.2f}%"),
            ("Alpha", f"{performance_metrics.get('alpha', 0):.2f}%")
        ]
        
        for i, (label, value) in enumerate(metrics):
            x_pos = 300 if i % 2 == 0 else 900
            y_pos = metrics_y + (i // 2) * 70
            
            draw.text((x_pos, y_pos), f"{label}: {value}", 
                     fill=(60, 60, 60), font=regular_font, anchor="mm")
    
    # Add powered by text and date
    draw.text((width//2, height-100), f"Powered by IndiaQuant • Generated on {datetime.now().strftime('%d %b %Y')}", 
              fill=(100, 100, 100), font=small_font, anchor="mm")
    
    # Save to in-memory buffer
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def get_share_links(text_summary, image_data=None, title="My Portfolio Performance"):
    """
    Generate sharing links for various social media platforms
    
    Parameters:
    text_summary (str): Text to share
    image_data (BytesIO): Optional image data to share
    title (str): Title/subject for email sharing
    
    Returns:
    dict: Dictionary with share links for different platforms
    """
    # URL encode the text
    import urllib.parse
    encoded_text = urllib.parse.quote(text_summary)
    encoded_title = urllib.parse.quote(title)
    
    # Generate sharing links
    share_links = {
        'twitter': f"https://twitter.com/intent/tweet?text={encoded_text}",
        'whatsapp': f"https://api.whatsapp.com/send?text={encoded_text}",
        'telegram': f"https://t.me/share/url?url=https://indiaquant.com&text={encoded_text}",
        'email': f"mailto:?subject={encoded_title}&body={encoded_text}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url=https://indiaquant.com&summary={encoded_text}",
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u=https://indiaquant.com&quote={encoded_text}",
        'copy': text_summary
    }
    
    return share_links

def send_sms_update(phone_number, text_summary):
    """
    Send portfolio summary via SMS using Twilio
    
    Parameters:
    phone_number (str): Target phone number in E.164 format (e.g., +91XXXXXXXXXX)
    text_summary (str): Text to send
    
    Returns:
    dict: Response information
    """
    import os
    from twilio.rest import Client
    
    # Get Twilio credentials from environment variables
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
    
    if not all([account_sid, auth_token, twilio_phone]):
        return {
            'success': False,
            'message': 'Twilio credentials not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables.'
        }
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Truncate message if too long for SMS
        max_sms_length = 1600  # SMS can typically hold up to 1600 characters
        if len(text_summary) > max_sms_length:
            text_summary = text_summary[:max_sms_length-20] + "... [Truncated]"
        
        # Send the message
        message = client.messages.create(
            body=text_summary,
            from_=twilio_phone,
            to=phone_number
        )
        
        return {
            'success': True,
            'message': f'SMS sent successfully. SID: {message.sid}',
            'sid': message.sid
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error sending SMS: {str(e)}'
        }

def generate_qr_code(text):
    """
    Generate a QR code for the given text
    
    Parameters:
    text (str): Text to encode in QR code
    
    Returns:
    BytesIO: QR code image in memory buffer
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to in-memory buffer
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def get_image_download_link(img_bytes, filename="portfolio_summary.png", text="Download Image"):
    """
    Generate an HTML download link for an image
    
    Parameters:
    img_bytes (BytesIO): Image in memory buffer
    filename (str): Download filename
    text (str): Link text
    
    Returns:
    str: HTML download link
    """
    b64 = base64.b64encode(img_bytes.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">{text}</a>'
    return href

# End of file