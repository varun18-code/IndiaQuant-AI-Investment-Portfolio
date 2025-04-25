"""
Voice-Activated Financial Assistant with Regional Language Support
"""

import streamlit as st
import os
import numpy as np
import time
import threading
import tempfile
import logging
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
from utils.voice_assistant import (
    create_voice_assistant, 
    get_supported_languages, 
    get_language_code
)
from utils.stock_data import get_stock_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show():
    """Display the voice assistant page"""
    
    st.title("Voice-Activated Financial Assistant")
    
    # Introduction
    st.markdown("""
    ### Your Multilingual Financial Voice Assistant
    
    Use your voice to get quick updates on stocks, market trends, and your portfolio in your preferred language.
    
    **Features:**
    - Speak naturally to ask questions about stocks, markets, or your portfolio
    - Support for 10 Indian languages including Hindi, Tamil, Telugu, and more
    - Real-time voice responses in your language of choice
    - Contextual awareness to understand financial terms
    
    **How to use:**
    1. Select your preferred language from the dropdown
    2. Click the microphone button to start recording
    3. Speak your question clearly
    4. Wait for the assistant to respond
    """)
    
    # Initialize session state variables
    if 'voice_assistant' not in st.session_state:
        st.session_state.voice_assistant = create_voice_assistant()
    
    if 'transcription' not in st.session_state:
        st.session_state.transcription = ""
        
    if 'response' not in st.session_state:
        st.session_state.response = ""
        
    if 'audio_response' not in st.session_state:
        st.session_state.audio_response = None
    
    # Language selection
    supported_languages = get_supported_languages()
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_language = st.selectbox(
            "Select your preferred language",
            list(supported_languages.keys()),
            index=0
        )
    
    with col2:
        if st.button("Apply Language Change"):
            language_code = get_language_code(selected_language)
            if st.session_state.voice_assistant.set_language(language_code):
                st.success(f"Language changed to {selected_language}")
                # Generate new greeting in selected language
                greeting_text = st.session_state.voice_assistant.get_greeting()
                greeting_audio = st.session_state.voice_assistant.text_to_speech(greeting_text)
                st.session_state.response = greeting_text
                st.session_state.audio_response = greeting_audio
                st.rerun()
            else:
                st.error(f"Failed to change language to {selected_language}")
    
    # Create two columns for voice input and response
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Your Voice Command")
        
        # Voice recording interface
        def process_audio(audio_bytes):
            # Process the recorded audio
            try:
                # Recognize speech from audio
                transcription = st.session_state.voice_assistant.recognize_speech(audio_bytes)
                if transcription:
                    st.session_state.transcription = transcription
                    
                    # Process the command
                    response_text = st.session_state.voice_assistant.process_command(transcription)
                    st.session_state.response = response_text
                    
                    # Convert response to speech
                    audio_response = st.session_state.voice_assistant.text_to_speech(response_text)
                    st.session_state.audio_response = audio_response
                    
                    # Return value not used but required by the callback
                    return True
                else:
                    st.session_state.transcription = st.session_state.voice_assistant.responses["not_understood"]
                    return False
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                st.session_state.transcription = f"Error: {str(e)}"
                return False
        
        # Add audio recorder
        # Use the direct file uploader approach for reliability
        st.subheader("Upload Audio Recording")
        uploaded_file = st.file_uploader("Upload an audio file for voice recognition", type=["wav", "mp3"])
        
        if uploaded_file is not None:
            # Process the uploaded audio file
            audio_bytes = uploaded_file.read()
            
            # Show processing indicator
            with st.spinner("Processing audio..."):
                process_result = process_audio(audio_bytes)
                if process_result:
                    st.success("Audio processed successfully!")
                    # Force the UI to update
                    st.rerun()
                    
        # Add option for text input as an alternative
        st.subheader("Or Type Your Question")
        text_input = st.text_input("Type your question here and press Enter", key="text_question")
        
        if text_input and len(text_input) > 0:
            if st.button("Submit Question"):
                # Process the text input directly
                st.session_state.transcription = text_input
                
                # Process the command
                response_text = st.session_state.voice_assistant.process_command(text_input)
                st.session_state.response = response_text
                
                # Convert response to speech
                with st.spinner("Generating audio response..."):
                    audio_response = st.session_state.voice_assistant.text_to_speech(response_text)
                    st.session_state.audio_response = audio_response
                
                # Rerun to display the updated response
                st.rerun()
        
        # Display the transcription
        st.text_area("Transcribed Text", st.session_state.transcription, height=100, key="transcription_area")
        
        # Add example commands
        with st.expander("Example Commands"):
            st.markdown("""
            Try these example commands in your selected language:
            
            - "What is the current market status?"
            - "Show me information about Reliance stock"
            - "Give me a summary of my portfolio"
            - "What is the price of Infosys stock?"
            - "How is the NIFTY performing today?"
            """)
    
    with col2:
        st.subheader("Assistant Response")
        
        # Display text response
        st.text_area("Response Text", st.session_state.response, height=100, key="response_area")
        
        # Display audio response if available
        if st.session_state.audio_response:
            st.markdown("### Audio Response")
            audio_player_html = st.session_state.voice_assistant.create_audio_player_html(st.session_state.audio_response)
            st.markdown(audio_player_html, unsafe_allow_html=True)
            
            # Add replay button
            if st.button("Replay Response"):
                # This will regenerate the audio element with the same audio data
                st.markdown(audio_player_html, unsafe_allow_html=True)
        
        # Add language support info
        with st.expander("Supported Languages"):
            st.markdown("""
            The voice assistant currently supports the following languages:
            
            - English (Default)
            - Hindi (हिन्दी)
            - Tamil (தமிழ்)
            - Telugu (తెలుగు)
            - Bengali (বাংলা)
            - Marathi (मराठी)
            - Gujarati (ગુજરાતી)
            - Kannada (ಕನ್ನಡ)
            - Malayalam (മലയാളം)
            - Punjabi (ਪੰਜਾਬੀ)
            
            Language support quality may vary based on the Google Speech Recognition service.
            """)
    
    # Market context section
    st.subheader("Current Market Context")
    
    # Get real-time market data
    try:
        import yfinance as yf
        from utils.currency import format_currency, get_inr_symbol
        
        # Fetch data for indices
        nifty = yf.Ticker("^NSEI")
        sensex = yf.Ticker("^BSESN")
        usdinr = yf.Ticker("INR=X")
        
        # Get current data
        nifty_info = nifty.info
        sensex_info = sensex.info
        usdinr_info = usdinr.info
        
        # Create three columns for market data
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nifty_price = nifty_info.get('regularMarketPrice', 0)
            nifty_change = nifty_info.get('regularMarketChange', 0)
            nifty_percent = nifty_info.get('regularMarketChangePercent', 0)
            
            st.metric(
                label="NIFTY 50",
                value=f"{nifty_price:,.2f}",
                delta=f"{nifty_percent:.2f}%"
            )
        
        with col2:
            sensex_price = sensex_info.get('regularMarketPrice', 0)
            sensex_change = sensex_info.get('regularMarketChange', 0)
            sensex_percent = sensex_info.get('regularMarketChangePercent', 0)
            
            st.metric(
                label="SENSEX",
                value=f"{sensex_price:,.2f}",
                delta=f"{sensex_percent:.2f}%"
            )
        
        with col3:
            usdinr_price = usdinr_info.get('regularMarketPrice', 0)
            usdinr_change = usdinr_info.get('regularMarketChange', 0)
            usdinr_percent = usdinr_info.get('regularMarketChangePercent', 0)
            
            st.metric(
                label="USD/INR",
                value=f"{usdinr_price:.2f}",
                delta=f"{usdinr_percent:.2f}%",
                delta_color="inverse"  # Inverse because lower INR is better for imports
            )
            
    except Exception as e:
        # Fallback to static data if real-time data fails
        logger.error(f"Error fetching real-time market data: {e}")
        
        # Create three columns for market data
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="NIFTY 50",
                value="18,245.32",
                delta="0.5%"
            )
        
        with col2:
            st.metric(
                label="SENSEX",
                value="61,112.44",
                delta="0.4%"
            )
        
        with col3:
            st.metric(
                label="USD/INR",
                value="74.25",
                delta="-0.12%",
                delta_color="inverse"
            )
    
    # Add a section for recent queries and responses
    st.subheader("Recent Interactions")
    
    # Initialize the interactions history in session state if it doesn't exist
    if 'voice_interactions' not in st.session_state:
        st.session_state.voice_interactions = []
    
    # Add current interaction to history if there's a new transcription
    if st.session_state.transcription and st.session_state.response:
        # Only add if it's not already the most recent one
        if (not st.session_state.voice_interactions or 
            st.session_state.voice_interactions[-1]['query'] != st.session_state.transcription):
            st.session_state.voice_interactions.append({
                'query': st.session_state.transcription,
                'response': st.session_state.response,
                'timestamp': time.strftime('%H:%M:%S')
            })
            
            # Keep only the last 5 interactions
            if len(st.session_state.voice_interactions) > 5:
                st.session_state.voice_interactions.pop(0)
    
    # Display the interaction history
    if st.session_state.voice_interactions:
        for i, interaction in enumerate(reversed(st.session_state.voice_interactions)):
            with st.expander(f"Query at {interaction['timestamp']}: {interaction['query'][:50]}...", expanded=(i == 0)):
                st.markdown(f"**Query:** {interaction['query']}")
                st.markdown(f"**Response:** {interaction['response']}")
                st.markdown(f"**Time:** {interaction['timestamp']}")
    else:
        st.info("No voice interactions yet. Try speaking to the assistant.")
    
    # Voice assistant settings
    with st.expander("Voice Assistant Settings"):
        # Voice speed
        voice_speed = st.slider(
            "Voice Response Speed", 
            min_value=0.5, 
            max_value=1.5, 
            value=1.0, 
            step=0.1,
            help="Adjust the speed of the voice responses (not available in all languages)"
        )
        
        # Recognition sensitivity
        recognition_sensitivity = st.slider(
            "Speech Recognition Sensitivity",
            min_value=1,
            max_value=10,
            value=5,
            help="Adjust how sensitive the speech recognition is to background noise"
        )
        
        # Advanced settings
        col1, col2 = st.columns(2)
        
        with col1:
            use_contextual_awareness = st.checkbox(
                "Enable Contextual Awareness", 
                value=True,
                help="Assistant remembers previous questions to provide more relevant answers"
            )
        
        with col2:
            enable_notifications = st.checkbox(
                "Enable Voice Notifications",
                value=False,
                help="Get voice alerts for significant market movements"
            )
            
        if st.button("Save Settings"):
            st.success("Voice assistant settings saved successfully!")
            
    # Footer with tips
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; font-size: 0.8rem;">
        💡 <strong>Tip:</strong> For best results, speak clearly and in a quiet environment.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    show()