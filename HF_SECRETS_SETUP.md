# Setting Up Secrets in Hugging Face Space

To make your Reddit Scraper fully functional, you need to configure Reddit API credentials in your Hugging Face Space. This guide explains how to set up these secrets.

## Reddit API Credentials Needed

You need to obtain the following credentials from the [Reddit Developer Portal](https://www.reddit.com/prefs/apps):

1. `REDDIT_CLIENT_ID` - Your Reddit API client ID
2. `REDDIT_CLIENT_SECRET` - Your Reddit API client secret
3. `REDDIT_USER_AGENT` - (Optional) A custom user agent string

## Steps to Configure Secrets in Hugging Face Space

1. Go to your Hugging Face Space: https://huggingface.co/spaces/milwright/reddit-scraper
2. Click on the "Settings" tab at the top of the page
3. Scroll down to the "Repository secrets" section
4. Add each of the following secrets:

   - **Secret name**: `REDDIT_CLIENT_ID`  
     **Secret value**: Your Reddit API client ID

   - **Secret name**: `REDDIT_CLIENT_SECRET`  
     **Secret value**: Your Reddit API client secret

   - **Secret name**: `REDDIT_USER_AGENT`  
     **Secret value**: A custom user agent string (e.g., "RedditScraperApp/1.0")

5. Click "Add secret" after entering each one
6. Restart your Space by going to the "Factory" tab and clicking "Restart Space" button

## Alternative: User Input Method

If you prefer not to store your credentials as secrets, the app also allows users to input their Reddit API credentials directly in the user interface. These can be saved to a local .env file for future use.

## Creating Your Own Reddit API Credentials

If you don't have Reddit API credentials:

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in the details:
   - **Name**: Your app name (e.g., "Reddit Scraper")
   - **App type**: Select "script"
   - **Description**: Brief description of your app
   - **About URL**: Can be left blank
   - **Redirect URI**: Use "http://localhost:8000" (doesn't need to be a real endpoint)
4. Click "Create app"
5. Your client ID is the string under the app name (after "personal use script")
6. Your client secret is listed as "secret"
