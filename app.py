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

# Now that page config is set, we can safely import the main function
from advanced_scraper_ui import main

# Run the app
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Error: {str(e)}")
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
