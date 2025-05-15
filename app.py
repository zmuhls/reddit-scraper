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

# Modified approach: Initialize the session state directly
if 'results' not in st.session_state:
    st.session_state['results'] = None
if 'scraper' not in st.session_state:
    st.session_state['scraper'] = None
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []
if 'filters' not in st.session_state:
    st.session_state['filters'] = {
        'min_score': 0,
        'date_from': None,
        'date_to': None,
        'show_only_with_comments': False
    }

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

# Display welcome message and credential information
if not os.environ.get("REDDIT_CLIENT_ID") and not os.environ.get("REDDIT_CLIENT_SECRET"):
    st.info("👋 Welcome to Reddit Scraper!")
    
    st.markdown("""
    ## Important: Reddit API Credentials Required
    
    This app requires you to provide your own Reddit API credentials to function. 
    You'll need to:
    
    1. Obtain your credentials from the [Reddit Developer Portal](https://www.reddit.com/prefs/apps)
    2. Enter them in the sidebar's "Reddit API Credentials" section
    
    ### Getting Reddit API Credentials:
    1. Go to https://www.reddit.com/prefs/apps
    2. Click "Create App" or "Create Another App" 
    3. Fill in the details (name, description)
    4. Select "script" as the application type
    5. Use "http://localhost:8000" as the redirect URI
    6. Click "Create app"
    7. Take note of the client ID and client secret
    
    ### Privacy Note
    Your credentials are never stored on our servers. If you're using a personal copy of this Space, 
    you can set them up as Space secrets for convenience.
    """)

# Run the main application
main()
