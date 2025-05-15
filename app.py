# Reddit Scraper Hugging Face Space Launcher
# This file serves as the entry point for our Hugging Face Space

import os
import streamlit as st
from dotenv import load_dotenv

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

# Import the main app after environment setup to ensure it has access to variables
from advanced_scraper_ui import main

# Run the main app
if __name__ == "__main__":
    main()
