import streamlit as st
import os
from dotenv import load_dotenv

# IMPORTANT: set_page_config must be the first Streamlit command called
st.set_page_config(
    page_title="Reddit Scraper",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization is now handled in advanced_scraper_ui.py

# Load environment variables
load_dotenv()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        color: #ff4500;
        margin-bottom: 1rem;
    }
    .card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #ddd;
    }
    .small-text {
        font-size: 0.8rem;
        color: #777;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Load Hugging Face secrets if available
try:
    client_id = st.secrets.get("REDDIT_CLIENT_ID", "")
    client_secret = st.secrets.get("REDDIT_CLIENT_SECRET", "")
    user_agent = st.secrets.get("REDDIT_USER_AGENT", "RedditScraperApp/1.0")
    
    # Set as environment variables for other modules to use
    if client_id:
        os.environ["REDDIT_CLIENT_ID"] = client_id
    if client_secret:
        os.environ["REDDIT_CLIENT_SECRET"] = client_secret
    if user_agent:
        os.environ["REDDIT_USER_AGENT"] = user_agent
except Exception as e:
    # No secrets configured, will fall back to user input
    pass

# Now that setup is complete, import the main function
from enhanced_scraper import EnhancedRedditScraper
from advanced_scraper_ui import main

# Welcome message is now handled in advanced_scraper_ui.py in the Credentials tab

# Run the main application
main()
