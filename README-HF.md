# Reddit Scraper

![Reddit Scraper Logo](https://raw.githubusercontent.com/huggingface/hub-docs/main/static/icons/streamlit.svg)

A comprehensive tool for scraping Reddit data with a user-friendly interface for data collection, analysis, and visualization.

## Features

- 🔍 **Search multiple subreddits** simultaneously
- 🔑 **Filter posts by keywords** and various criteria  
- 📊 **Visualize data** with interactive charts
- 💾 **Export results** to CSV or JSON
- 📜 **Track search history**
- 🔐 **Secure credentials** management

## How to Use

### 1. Set up Reddit API Credentials

To use this app, you will need Reddit API credentials. You can get these from the [Reddit Developer Portal](https://www.reddit.com/prefs/apps).

- Click "Create App" or "Create Another App"
- Fill in the details (name, description)
- Select "script" as the application type
- Use "http://localhost:8000" as the redirect URI (this doesn't need to be a real endpoint)
- Click "Create app"
- Take note of the client ID (the string under "personal use script") and client secret

Enter these credentials in the app's sidebar or set them up as secrets in the Hugging Face Space settings (if you've duplicated this Space).

### 2. Searching Reddit

1. Enter one or more subreddits to search (one per line)
2. Specify keywords to search for (one per line)
3. Adjust parameters like post limit, sorting method, etc.
4. Click "Run Search" to start scraping

### 3. Working with Results

- Use the tabs to navigate between different views
- Apply additional filters to the search results
- Visualize the data with built-in charts
- Export results to CSV or JSON for further analysis

## Privacy & API Usage

This tool uses the official Reddit API and follows Reddit's API terms of service. Your API credentials are never stored on our servers unless you explicitly save them to your own copy of this Space.

## Setup Your Own Copy

If you want to run this app with your own credentials always available:

1. Duplicate this Space to your account
2. Go to Settings → Repository Secrets
3. Add the following secrets:
   - `REDDIT_CLIENT_ID`: Your Reddit API client ID
   - `REDDIT_CLIENT_SECRET`: Your Reddit API client secret
   - `REDDIT_USER_AGENT`: (Optional) A custom user agent string

## Tech Stack

- [Streamlit](https://streamlit.io/): UI framework
- [PRAW](https://praw.readthedocs.io/): Reddit API wrapper
- [Pandas](https://pandas.pydata.org/): Data processing
- [Plotly](https://plotly.com/): Data visualization

## Feedback & Contributions

If you find any issues or have suggestions for improvements, please open an issue on the [GitHub repository](https://github.com/yourusername/reddit-scraper) or create a discussion on this Hugging Face Space.
