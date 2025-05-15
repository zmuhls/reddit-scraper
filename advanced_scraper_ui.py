# Add warning suppression at the very beginning before any other imports
import warnings
warnings.filterwarnings("ignore", message="No secrets files found.*")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import time
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from enhanced_scraper import EnhancedRedditScraper

# Note: Page configuration and session state initialization are handled in app.py

# Functions
def initialize_scraper(client_id, client_secret, user_agent):
    """Initialize the scraper with API credentials"""
    try:
        scraper = EnhancedRedditScraper(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        st.session_state.scraper = scraper
        return True
    except Exception as e:
        st.error(f"Failed to initialize scraper: {str(e)}")
        return False

def run_search(subreddits, keywords, limit, sort_by, include_comments, 
               include_selftext, min_score):
    """Run the search with provided parameters"""
    if not st.session_state.scraper:
        st.error("Scraper not initialized. Please set up API credentials first.")
        return False
    
    try:
        with st.spinner("Scraping Reddit..."):
            if len(subreddits) == 1:
                # Single subreddit search
                results = st.session_state.scraper.scrape_subreddit(
                    subreddit_name=subreddits[0],
                    keywords=keywords,
                    limit=limit,
                    sort_by=sort_by,
                    include_comments=include_comments,
                    include_selftext=include_selftext,
                    min_score=min_score
                )
                st.session_state.results = {subreddits[0]: results}
            else:
                # Multiple subreddit search
                results = st.session_state.scraper.search_multiple_subreddits(
                    subreddits=subreddits,
                    keywords=keywords,
                    limit=limit,
                    sort_by=sort_by,
                    include_comments=include_comments,
                    include_selftext=include_selftext,
                    min_score=min_score
                )
                st.session_state.results = results
            
            # Add to search history
            search_info = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'subreddits': subreddits,
                'keywords': keywords,
                'total_results': sum(len(results) for results in st.session_state.results.values())
            }
            st.session_state.search_history.append(search_info)
            
            return True
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        return False

def filter_results(results, filters):
    """Apply filters to results"""
    filtered = {}
    
    for subreddit, posts in results.items():
        filtered_posts = []
        
        for post in posts:
            # Apply score filter
            if post['score'] < filters['min_score']:
                continue
                
            # Apply date filters if set
            if filters['date_from'] or filters['date_to']:
                post_date = datetime.strptime(post['created_utc'], '%Y-%m-%d %H:%M:%S')
                
                if filters['date_from'] and post_date < filters['date_from']:
                    continue
                if filters['date_to'] and post_date > filters['date_to']:
                    continue
            
            # Filter for posts with comments if requested
            if filters['show_only_with_comments'] and (
                'matching_comments' not in post or not post['matching_comments']):
                continue
                
            filtered_posts.append(post)
            
        filtered[subreddit] = filtered_posts
    
    return filtered

def create_data_visualization(results):
    """Create data visualizations based on results"""
    # Combine all results
    all_posts = []
    for subreddit, posts in results.items():
        for post in posts:
            post['subreddit'] = subreddit
            all_posts.append(post)
    
    if not all_posts:
        st.warning("No data to visualize.")
        return
    
    df = pd.DataFrame(all_posts)
    
    # Create tabs for different visualizations
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Score Distribution", "Posts by Subreddit", "Time Analysis"])
    
    with viz_tab1:
        st.subheader("Score Distribution")
        fig = px.histogram(df, x="score", color="subreddit", nbins=20,
                          title="Distribution of Post Scores")
        st.plotly_chart(fig, use_container_width=True)
    
    with viz_tab2:
        st.subheader("Posts by Subreddit")
        subreddit_counts = df['subreddit'].value_counts().reset_index()
        subreddit_counts.columns = ['subreddit', 'count']
        fig = px.bar(subreddit_counts, x='subreddit', y='count',
                     title="Number of Matching Posts by Subreddit")
        st.plotly_chart(fig, use_container_width=True)
    
    with viz_tab3:
        st.subheader("Time Analysis")
        # Convert created_utc to datetime if it's not already
        if 'created_utc' in df.columns:
            df['created_date'] = pd.to_datetime(df['created_utc'])
            df['hour_of_day'] = df['created_date'].dt.hour
            
            fig = px.histogram(df, x="hour_of_day", nbins=24,
                              title="Posts by Hour of Day")
            fig.update_layout(xaxis_title="Hour of Day (UTC)")
            st.plotly_chart(fig, use_container_width=True)

def main():
    # Suppress the "No secrets files found" warning
    warnings.filterwarnings("ignore", message="No secrets files found.*")
    
    # Ensure session state variables are initialized
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
    
    # Header
    st.markdown('<div class="main-header">Reddit Scraper</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Data Collection Tool</div>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        
        # Search Parameters
        st.subheader("Search Parameters")
        
        # Multiple subreddit input
        subreddits_input = st.text_area("Subreddits (one per line)", value="cuny\ncollegequestions")
        subreddits = [s.strip() for s in subreddits_input.split("\n") if s.strip()]
        
        # Keywords input
        keywords_input = st.text_area("Keywords (one per line)", value="question\nhelp\nconfused")
        keywords = [k.strip() for k in keywords_input.split("\n") if k.strip()]
        
        # Other parameters
        limit = st.slider("Number of posts to scan per subreddit", 10, 200, 50)
        sort_by = st.selectbox("Sort posts by", ["hot", "new", "top", "rising"], index=0)
        include_selftext = st.checkbox("Include post content in search", value=True)
        include_comments = st.checkbox("Include comments in search", value=True)
        min_score = st.slider("Minimum score (upvotes)", 0, 1000, 0)
        
        # Action buttons
        search_col, clear_col = st.columns(2)
        with search_col:
            search_button = st.button("Run Search", type="primary", use_container_width=True)
        with clear_col:
            clear_button = st.button("Clear Results", type="secondary", use_container_width=True)
    
    # Main interface tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Results", "Visualizations", "Export", "History", "API Credentials"])
    
    # Handle Actions
    if clear_button:
        st.session_state.results = None
        st.rerun()
    
    if search_button:
        if not subreddits:
            st.error("Please enter at least one subreddit to search.")
        elif not keywords:
            st.error("Please enter at least one keyword to search.")
        else:
            success = run_search(
                subreddits=subreddits,
                keywords=keywords,
                limit=limit,
                sort_by=sort_by,
                include_comments=include_comments,
                include_selftext=include_selftext,
                min_score=min_score
            )
            if success:
                st.success(f"Search completed! Found results in {len(st.session_state.results)} subreddits.")
    
    # Tab 1: Results
    with tab1:
        if st.session_state.results:
            # Post-search filters
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Filter Results")
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                st.session_state.filters['min_score'] = st.number_input(
                    "Minimum score", min_value=0, value=st.session_state.filters['min_score'])
            
            with filter_col2:
                st.session_state.filters['date_from'] = st.date_input(
                    "From date", value=None)
            
            with filter_col3:
                st.session_state.filters['date_to'] = st.date_input(
                    "To date", value=None)
            
            st.session_state.filters['show_only_with_comments'] = st.checkbox(
                "Show only posts with matching comments", 
                value=st.session_state.filters['show_only_with_comments'])
            
            apply_filters = st.button("Apply Filters")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Apply filters if requested
            if apply_filters:
                filtered_results = filter_results(st.session_state.results, st.session_state.filters)
            else:
                filtered_results = st.session_state.results
            
            # Show results for each subreddit
            total_posts = sum(len(posts) for posts in filtered_results.values())
            st.subheader(f"Search Results ({total_posts} posts found)")
            
            for subreddit, posts in filtered_results.items():
                with st.expander(f"r/{subreddit} - {len(posts)} posts", expanded=len(filtered_results) == 1):
                    if posts:
                        # Create a dataframe for easier viewing
                        df = pd.DataFrame([{
                            'Title': p['title'], 
                            'Score': p['score'],
                            'Comments': p['num_comments'],
                            'Date': p['created_utc'],
                            'URL': p['permalink']
                        } for p in posts])
                        
                        st.dataframe(df, use_container_width=True)
                        
                        # Show detailed post view
                        st.subheader("Post Details")
                        post_index = st.slider(f"Select post from r/{subreddit}", 
                                                0, max(0, len(posts)-1), 0)
                        
                        if len(posts) > 0:
                            post = posts[post_index]
                            
                            # Display post details in a card
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            st.markdown(f"### {post['title']}")
                            st.markdown(f"**Author:** u/{post['author']} | **Score:** {post['score']} | **Comments:** {post['num_comments']}")
                            st.markdown(f"**Posted on:** {post['created_utc']}")
                            st.markdown(f"**URL:** [{post['url']}]({post['url']})")
                            
                            if post['text']:
                                st.markdown("##### Post Content")
                                with st.container():
                                    show_content = st.checkbox("Show full content", key=f"content_{subreddit}_{post_index}")
                                    if show_content:
                                        st.text(post['text'])
                            
                            # Show matching comments if available
                            if 'matching_comments' in post and post['matching_comments']:
                                st.markdown(f"##### Matching Comments ({len(post['matching_comments'])})")
                                with st.container():
                                    show_comments = st.checkbox("Show comments", value=True, key=f"comments_{subreddit}_{post_index}")
                                    if show_comments:
                                        for i, comment in enumerate(post['matching_comments']):
                                            st.markdown(f"**u/{comment['author']}** ({comment['score']} points) - {comment['created_utc']}")
                                            st.text(comment['body'])
                                            if i < len(post['matching_comments']) - 1:
                                                st.divider()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info(f"No posts found in r/{subreddit} matching the current filters.")
        else:
            st.info("Configure the search parameters and click 'Run Search' to begin.")
            
            # Show help for first-time users
            with st.expander("Help & Tips"):
                st.markdown("""
                ### Quick Start Guide
                
                1. Set up your **API credentials** in the API Credentials tab
                2. Enter **subreddits** to search (one per line)
                3. Enter **keywords** to filter posts (one per line)
                4. Adjust settings as needed
                5. Click **Run Search**
                
                ### Search Tips
                
                - Use specific keywords for targeted results
                - Search multiple related subreddits for better coverage
                - Enable comment search to find keywords in discussions
                - Use visualizations to identify trends
                - Export data for external analysis
                """)
    
    # Tab 2: Visualizations
    with tab2:
        if st.session_state.results:
            # Apply current filters to visualization data
            filtered_results = filter_results(st.session_state.results, st.session_state.filters)
            create_data_visualization(filtered_results)
        else:
            st.info("Run a search to generate visualizations.")
    
    # Tab 3: Export
    with tab3:
        if st.session_state.results:
            st.subheader("Export Results")
            
            # Apply current filters
            filtered_results = filter_results(st.session_state.results, st.session_state.filters)
            
            # Format selection
            export_format = st.radio("Export format", ["CSV", "JSON"], horizontal=True)
            
            # Filename input
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            default_filename = f"reddit_scrape_{timestamp}"
            filename = st.text_input("Filename (without extension)", value=default_filename)
            
            # Export button
            export_clicked = st.button("Export Data", type="primary")
            
            if export_clicked:
                try:
                    # Combine all results into a flat list for export
                    all_results = []
                    for subreddit, posts in filtered_results.items():
                        for post in posts:
                            post_copy = post.copy()
                            post_copy['subreddit'] = subreddit
                            all_results.append(post_copy)
                    
                    # Save results based on selected format
                    if export_format == "CSV":
                        # Convert to dataframe and save
                        df = pd.DataFrame(all_results)
                        
                        # Handle nested structures for CSV
                        if 'matching_comments' in df.columns:
                            df['matching_comments'] = df['matching_comments'].apply(
                                lambda x: json.dumps(x) if isinstance(x, list) else ''
                            )
                        
                        csv_file = f"{filename}.csv"
                        df.to_csv(csv_file, index=False)
                        
                        # Create download button
                        with open(csv_file, 'rb') as f:
                            st.download_button(
                                label="Download CSV",
                                data=f,
                                file_name=csv_file,
                                mime="text/csv"
                            )
                        st.success(f"Exported {len(all_results)} posts to {csv_file}")
                        
                    else:  # JSON
                        json_file = f"{filename}.json"
                        with open(json_file, 'w') as f:
                            json.dump(all_results, f, indent=2)
                        
                        # Create download button
                        with open(json_file, 'rb') as f:
                            st.download_button(
                                label="Download JSON",
                                data=f,
                                file_name=json_file,
                                mime="application/json"
                            )
                        st.success(f"Exported {len(all_results)} posts to {json_file}")
                        
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
        else:
            st.info("Run a search to export results.")
    
    # Tab 4: History
    with tab4:
        st.subheader("Search History")
        
        if st.session_state.search_history:
            for i, search in enumerate(reversed(st.session_state.search_history)):
                with st.expander(f"Search #{len(st.session_state.search_history)-i}: {search['timestamp']} ({search['total_results']} results)"):
                    st.markdown(f"**Subreddits:** {', '.join(search['subreddits'])}")
                    st.markdown(f"**Keywords:** {', '.join(search['keywords'])}")
                    st.markdown(f"**Results:** {search['total_results']} posts")
                    st.markdown(f"**Time:** {search['timestamp']}")
        else:
            st.info("No search history yet.")
            
    # Tab 5: API Credentials - Auto-closed by default
    with tab5:
        # Display welcome message and credential information if credentials are not set
        if not os.environ.get("REDDIT_CLIENT_ID") and not os.environ.get("REDDIT_CLIENT_SECRET"):
            st.info("👋 Welcome to Reddit Scraper!")
            
            st.subheader("Reddit API Credentials")
            
            st.markdown("""
            ### Reddit API Credentials Required
            
            This app requires your Reddit API credentials to function.""")
        
        # Two columns for instructions and input
        cred_col1, cred_col2 = st.columns([1, 1])
        
        with cred_col1:
            st.markdown("""
            #### Getting Credentials:
            1. Go to [Reddit Developer Portal](https://www.reddit.com/prefs/apps)
            2. Click "Create App" or "Create Another App"
            3. Fill in details (name, description)
            4. Select "script" as application type
            5. Use "http://localhost:8000" as redirect URI
            6. Click "Create app"
            7. Note the client ID and secret
            
            #### Privacy Note
            Your credentials are never stored on any servers. For personal copies, 
            you can set them as Space secrets.
            """)
            
        with cred_col2:
            # Initialize session state for credentials if they don't exist
            if 'client_id' not in st.session_state:
                st.session_state.client_id = ""
            if 'client_secret' not in st.session_state:
                st.session_state.client_secret = ""
            if 'user_agent' not in st.session_state:
                st.session_state.user_agent = "RedditScraperApp/1.0"
            
            # In development environment, try to load from .env file for convenience
            # But don't do this in production to avoid credential leakage
            is_local_dev = not os.environ.get('SPACE_ID') and not os.environ.get('SYSTEM')
            if is_local_dev:
                load_dotenv()
                # Only load from env if session state is empty (first load)
                if not st.session_state.client_id:
                    st.session_state.client_id = os.environ.get("REDDIT_CLIENT_ID", "")
                if not st.session_state.client_secret:
                    st.session_state.client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
                if st.session_state.user_agent == "RedditScraperApp/1.0":
                    st.session_state.user_agent = os.environ.get("REDDIT_USER_AGENT", "RedditScraperApp/1.0")
            
            # Use session state for the input values
            client_id = st.text_input("Client ID", value=st.session_state.client_id, key="client_id_input")
            client_secret = st.text_input("Client Secret", value=st.session_state.client_secret, type="password", key="client_secret_input")
            user_agent = st.text_input("User Agent", value=st.session_state.user_agent, key="user_agent_input")
            
            # Update session state when input changes
            st.session_state.client_id = client_id
            st.session_state.client_secret = client_secret
            st.session_state.user_agent = user_agent
            
            if st.button("Initialize API Connection", type="primary"):
                if initialize_scraper(client_id, client_secret, user_agent):
                    st.success("API connection established!")
                    # Set environment variables for the current session
                    os.environ["REDDIT_CLIENT_ID"] = client_id
                    os.environ["REDDIT_CLIENT_SECRET"] = client_secret
                    os.environ["REDDIT_USER_AGENT"] = user_agent

if __name__ == "__main__":
    main()
