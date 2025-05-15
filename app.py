# Reddit Scraper Hugging Face Space Launcher
# This file serves as the entry point for our Hugging Face Space

import os
import streamlit as st
from dotenv import load_dotenv

# Configure Streamlit page
st.set_page_config(
    page_title="Reddit Scraper",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables from .streamlit/secrets.toml if in Hugging Face Space Environment
def load_huggingface_secrets():
    try:
        # HF Spaces store secrets in st.secrets
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
            
        return True
    except Exception:
        # Fallback to regular .env file if not in HF Space
        return False

# Try to load secrets (first from HF secrets, then from .env)
load_huggingface_secrets()
load_dotenv()

# Add custom CSS
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

# Now import functions from the UI module
# But not the whole file to avoid st.set_page_config being called twice
import sys
import importlib.util

# Import individual functions from advanced_scraper_ui
spec = importlib.util.spec_from_file_location("advanced_scraper_ui", "advanced_scraper_ui.py")
ui_module = importlib.util.module_from_spec(spec)
sys.modules["advanced_scraper_ui"] = ui_module
spec.loader.exec_module(ui_module)

# Run the main app
if __name__ == "__main__":
    try:
        # Call the main function without re-importing the whole module
        ui_module.main()
    except Exception as e:
        st.error(f"Error running the application: {str(e)}")
        st.error("This might be due to missing Reddit API credentials.")
        
        # Display instructions for setting up credentials
        st.markdown("""
        ## Setting up Reddit API Credentials
        
        This app requires Reddit API credentials to function properly. You can:
        
        1. Enter your credentials directly in the sidebar when the app loads, or
        2. Set them up as Hugging Face Space secrets (if you've duplicated this Space)
        
        To obtain Reddit API credentials:
        1. Go to https://www.reddit.com/prefs/apps
        2. Click "Create App" or "Create Another App" 
        3. Fill in the details and select "script" as the application type
        4. Use "http://localhost:8000" as the redirect URI
        5. Take note of the client ID and client secret
        """)
