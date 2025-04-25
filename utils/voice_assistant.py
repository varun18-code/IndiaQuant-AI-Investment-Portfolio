"""
Voice Assistant module for IndiaQuant application
Provides voice input/output capabilities with regional language support
"""

import os
import tempfile
import threading
import time
import logging
import queue
import json
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supported Indian languages
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta", 
    "Telugu": "te",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa"
}

# Financial assistant responses for different language scenarios
RESPONSES = {
    "en": {
        "greeting": "Hello, I am your financial assistant. How can I help you?",
        "not_understood": "I'm sorry, I didn't understand that. Could you please repeat?",
        "processing": "I'm processing your request...",
        "farewell": "Thank you for using the voice assistant. Goodbye!",
        "error": "I encountered an error. Please try again.",
        "stock_info": "Here is the information for stock {}.",
        "market_update": "The market is currently {}. The NIFTY is at {} and SENSEX is at {}.",
        "portfolio_summary": "Your portfolio is currently valued at {} with a {} of {}% today."
    },
    "hi": {
        "greeting": "नमस्ते, मैं आपका वित्तीय सहायक हूं। मैं आपकी कैसे मदद कर सकता हूं?",
        "not_understood": "मुझे माफ करें, मुझे यह समझ नहीं आया। क्या आप दोहरा सकते हैं?",
        "processing": "मैं आपके अनुरोध पर काम कर रहा हूं...",
        "farewell": "वॉयस असिस्टेंट का उपयोग करने के लिए धन्यवाद। अलविदा!",
        "error": "मुझे एक त्रुटि मिली। कृपया पुन: प्रयास करें।",
        "stock_info": "{} स्टॉक के लिए यहां जानकारी है।",
        "market_update": "बाजार वर्तमान में {} है। निफ्टी {} पर है और सेंसेक्स {} पर है।",
        "portfolio_summary": "आपका पोर्टफोलियो वर्तमान में {} का है जिसमें आज {}% का {} है।"
    },
    "ta": {
        "greeting": "வணக்கம், நான் உங்கள் நிதி உதவியாளர். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        "not_understood": "மன்னிக்கவும், எனக்கு அது புரியவில்லை. நீங்கள் திரும்ப சொல்ல முடியுமா?",
        "processing": "உங்கள் கோரிக்கையை செயலாக்குகிறேன்...",
        "farewell": "குரல் உதவியாளரைப் பயன்படுத்தியதற்கு நன்றி. வணக்கம்!",
        "error": "ஒரு பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.",
        "stock_info": "பங்கு {} க்கான தகவல் இங்கே.",
        "market_update": "சந்தை தற்போது {} ஆக உள்ளது. நிஃப்டி {} இல் உள்ளது மற்றும் சென்செக்ஸ் {} இல் உள்ளது.",
        "portfolio_summary": "உங்கள் பங்குத்தொகுப்பு தற்போது {} மதிப்புடையது, இன்று {}% {} உள்ளது."
    }
}

# Add more languages as needed, with similar response templates

class VoiceAssistant:
    """
    Voice Assistant class for providing voice interface to IndiaQuant
    Supports multiple Indian languages for input/output
    """
    
    def __init__(self, language="en"):
        """
        Initialize the voice assistant
        
        Parameters:
        language (str): Language code for the voice assistant (default: "en" for English)
        """
        self.language = language
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self.responses = {}
        self.load_responses()
        
    def load_responses(self):
        """Load appropriate language responses"""
        self.responses = RESPONSES.get(self.language, RESPONSES["en"])
    
    def set_language(self, language):
        """
        Set the language for the voice assistant
        
        Parameters:
        language (str): Language code to set
        """
        if language in SUPPORTED_LANGUAGES.values():
            self.language = language
            self.load_responses()
            return True
        return False
    
    def recognize_speech(self, audio_bytes):
        """
        Convert speech to text
        
        Parameters:
        audio_bytes (bytes): Audio data to recognize
        
        Returns:
        str: Recognized text or None if recognition failed
        """
        temp_audio_path = None
        try:
            # Save the audio bytes to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            # Process the audio file
            with sr.AudioFile(temp_audio_path) as source:
                audio_data = self.recognizer.record(source)
                
                # Attempt to recognize speech using Google's Speech Recognition
                # Use the specified language for recognition
                text = self.recognizer.recognize_google(
                    audio_data, 
                    language=self.language
                )
                
                if temp_audio_path:
                    os.unlink(temp_audio_path)  # Delete the temporary file
                return text
        except sr.UnknownValueError:
            logger.error("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            
        # Delete the temporary file in case of an error
        if temp_audio_path:
            try:
                os.unlink(temp_audio_path)
            except:
                pass
            
        return None
    
    def text_to_speech(self, text):
        """
        Convert text to speech
        
        Parameters:
        text (str): Text to convert to speech
        
        Returns:
        bytes: Audio data for the speech
        """
        try:
            # Create a BytesIO object to store the audio data
            audio_bytes_io = BytesIO()
            
            # Generate the speech
            tts = gTTS(text=text, lang=self.language, slow=False)
            tts.write_to_fp(audio_bytes_io)
            
            # Reset the position to the beginning of the BytesIO object
            audio_bytes_io.seek(0)
            
            # Return the audio data
            return audio_bytes_io.read()
        except Exception as e:
            logger.error(f"Error in text to speech conversion: {e}")
            return None
    
    def create_audio_player_html(self, audio_bytes):
        """
        Create HTML for an audio player with the provided audio data
        
        Parameters:
        audio_bytes (bytes): Audio data to play
        
        Returns:
        str: HTML code for an audio player
        """
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio autoplay="true" controls>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        return audio_html
    
    def process_command(self, text):
        """
        Process a voice command and return a response
        
        Parameters:
        text (str): Command text to process
        
        Returns:
        str: Response to the command
        """
        import yfinance as yf
        from utils.currency import format_currency
        
        text_lower = text.lower()
        
        # Stock information request
        if "stock" in text_lower or "share" in text_lower or "price" in text_lower:
            # Extract stock name - this is a simple extraction, can be enhanced with NLP
            stock_name = None
            words = text_lower.split()
            for i, word in enumerate(words):
                if word in ["stock", "share", "price"] and i+1 < len(words):
                    stock_name = words[i+1].upper()
                    break
            
            if stock_name:
                try:
                    # Try to get real stock data
                    ticker = yf.Ticker(stock_name)
                    info = ticker.info
                    
                    if 'regularMarketPrice' in info or 'currentPrice' in info:
                        price = info.get('regularMarketPrice') or info.get('currentPrice', 0)
                        change = info.get('regularMarketChange') or info.get('change', 0)
                        change_percent = info.get('regularMarketChangePercent') or info.get('changePercent', 0)
                        
                        # Format the response with real data
                        custom_response = f"{stock_name} is currently trading at {price:.2f}, which is {change:.2f} ({change_percent:.2f}%) "
                        custom_response += "up" if change > 0 else "down"
                        custom_response += " today."
                        
                        return custom_response
                except Exception as e:
                    logger.error(f"Error getting stock data for {stock_name}: {e}")
                
                # Fallback to generic response if real data fails
                return self.responses["stock_info"].format(stock_name)
            
        # Market update request
        if "market" in text_lower or "nifty" in text_lower or "sensex" in text_lower:
            try:
                # Try to get real market data
                nifty_ticker = yf.Ticker("^NSEI")  # NIFTY 50
                sensex_ticker = yf.Ticker("^BSESN")  # SENSEX
                
                nifty_data = nifty_ticker.history(period="1d")
                sensex_data = sensex_ticker.history(period="1d")
                
                if not nifty_data.empty and not sensex_data.empty:
                    nifty_close = nifty_data['Close'][-1]
                    nifty_prev_close = nifty_data['Open'][0]
                    nifty_change = nifty_close - nifty_prev_close
                    nifty_change_percent = (nifty_change / nifty_prev_close) * 100
                    
                    sensex_close = sensex_data['Close'][-1]
                    sensex_prev_close = sensex_data['Open'][0]
                    sensex_change = sensex_close - sensex_prev_close
                    sensex_change_percent = (sensex_change / sensex_prev_close) * 100
                    
                    market_status = "up" if nifty_change > 0 else "down"
                    market_status += f" {abs(nifty_change_percent):.2f}%"
                    
                    return self.responses["market_update"].format(
                        market_status,
                        f"{nifty_close:.2f}",
                        f"{sensex_close:.2f}"
                    )
            except Exception as e:
                logger.error(f"Error getting market data: {e}")
            
            # Fallback to static data if real data fails
            market_status = "up 0.5%" 
            nifty = "18,245"
            sensex = "61,120"
            
            return self.responses["market_update"].format(market_status, nifty, sensex)
        
        # Portfolio summary request
        if "portfolio" in text_lower or "my investments" in text_lower:
            try:
                # In a real app, this would fetch the user's portfolio data from a database
                # Here we're simulating it
                import random
                from datetime import datetime
                
                # Simulate portfolio data
                portfolio_value = random.uniform(500000, 2000000)  # Random value between 5L and 20L
                daily_change = random.uniform(-2.0, 3.0)  # Random change between -2% and 3%
                
                change_type = "gain" if daily_change > 0 else "loss"
                change_percent = abs(daily_change)
                
                formatted_value = format_currency(portfolio_value) if 'format_currency' in locals() else f"₹{portfolio_value:,.2f}"
                
                return self.responses["portfolio_summary"].format(
                    formatted_value,
                    change_type,
                    f"{change_percent:.2f}"
                )
            except Exception as e:
                logger.error(f"Error getting portfolio data: {e}")
                
                # Fallback to static data
                portfolio_value = "₹10,25,000"
                change_type = "gain"
                change_percent = "1.2"
                
                return self.responses["portfolio_summary"].format(portfolio_value, change_type, change_percent)
        
        # Greeting
        if "hello" in text_lower or "hi" in text_lower or "hey" in text_lower or "namaste" in text_lower:
            return self.get_greeting()
            
        # Farewell
        if "goodbye" in text_lower or "bye" in text_lower or "thank you" in text_lower or "thanks" in text_lower:
            return self.get_farewell()
        
        # Default response if no specific command is detected
        return self.responses["not_understood"]
    
    def get_greeting(self):
        """Get the greeting in the current language"""
        return self.responses["greeting"]
    
    def get_farewell(self):
        """Get the farewell in the current language"""
        return self.responses["farewell"]

def get_supported_languages():
    """
    Get a list of supported languages
    
    Returns:
    dict: Dictionary of supported languages with their codes
    """
    return SUPPORTED_LANGUAGES

def get_language_code(language_name):
    """
    Get the language code for a language name
    
    Parameters:
    language_name (str): Name of the language
    
    Returns:
    str: Language code or None if not found
    """
    return SUPPORTED_LANGUAGES.get(language_name)

def create_voice_assistant(language="en"):
    """
    Create a new voice assistant instance
    
    Parameters:
    language (str): Language code for the voice assistant
    
    Returns:
    VoiceAssistant: A new voice assistant instance
    """
    return VoiceAssistant(language)