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

# Disable static file serving to prevent the warning
os.environ['STREAMLIT_SERVER_ENABLE_STATIC_SERVING'] = 'false'

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
    try:
        # Check if we have any data
        total_posts = sum(len(posts) for posts in results.values())
        if total_posts == 0:
            st.warning("No posts found matching your search criteria. Try adjusting your filters.")
            return
            
        # Combine all results
        all_posts = []
        skipped_posts = 0
        for subreddit, posts in results.items():
            for post in posts:
                try:
                    post_copy = post.copy()
                    post_copy['subreddit'] = subreddit
                    all_posts.append(post_copy)
                except Exception as e:
                    skipped_posts += 1
                    continue  # Skip this post but continue processing others
        
        if skipped_posts > 0:
            st.warning(f"Skipped {skipped_posts} post(s) due to formatting errors.")
            
        if not all_posts:
            st.warning("No valid data to visualize.")
            return
        
        # Create DataFrame
        df = pd.DataFrame(all_posts)
        
        # Basic data validation
        required_columns = ['score', 'subreddit']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Required column(s) missing: {', '.join(missing_columns)}")
            st.write("Available columns:", df.columns.tolist())
            return
        
        # Create tabs for different visualizations
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Score Distribution", "Posts by Subreddit", "Time Analysis"])
        
        # Score Distribution
        with viz_tab1:
            try:
                # Calculate a robust max score limit to handle extreme outliers
                # Use IQR method for better outlier detection
                q1 = df['score'].quantile(0.25)
                q3 = df['score'].quantile(0.75)
                iqr = q3 - q1
                upper_bound = q3 + 1.5 * iqr
                
                # Cap at either the IQR-based upper bound or 95th percentile * 2, whichever is larger
                # This gives a better visualization range while still showing important variations
                max_score_display = max(min(upper_bound, df['score'].max()), df['score'].quantile(0.95) * 2)
                
                # Filter dataframe for visualization
                filtered_df = df[df['score'] <= max_score_display]
                
                # Create histogram with automatic bin calculation
                nbins = min(20, len(filtered_df['score'].unique()))  # Adjust bins based on unique values
                
                fig = px.histogram(filtered_df, x="score", color="subreddit", nbins=nbins,
                                 title="Distribution of Post Scores")
                fig.update_layout(
                    xaxis_title="Score (Upvotes)",
                    yaxis_title="Number of Posts",
                    legend_title="Subreddit"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show excluded outliers info if any were filtered
                outliers_count = len(df) - len(filtered_df)
                if outliers_count > 0:
                    if outliers_count == 1:
                        highest_score = df['score'].max()
                        st.info(f"1 high-scoring outlier post (score: {highest_score}) was excluded for better visualization scale. Max displayed score: {int(max_score_display)}.")
                    else:
                        st.info(f"{outliers_count} high-scoring outlier posts were excluded for better visualization scale. Max displayed score: {int(max_score_display)}.")
            except Exception as e:
                st.error(f"Error creating score distribution chart: {str(e)}")
    
        # Posts by Subreddit
        with viz_tab2:
            try:
                # Get counts and sort by count for better visualization
                subreddit_counts = df['subreddit'].value_counts().reset_index()
                subreddit_counts.columns = ['subreddit', 'count']
                
                # Sort by count descending for better visualization
                subreddit_counts = subreddit_counts.sort_values('count', ascending=False)
                
                # Calculate average score per subreddit for additional insights
                subreddit_avg_scores = df.groupby('subreddit')['score'].mean().reset_index()
                subreddit_avg_scores.columns = ['subreddit', 'avg_score']
                
                # Merge the data
                subreddit_stats = subreddit_counts.merge(subreddit_avg_scores, on='subreddit')
                
                # Create bar chart
                fig = px.bar(subreddit_stats, x='subreddit', y='count',
                           title="Number of Matching Posts by Subreddit",
                           hover_data=['avg_score'],
                           color='avg_score',
                           color_continuous_scale='Viridis')
                
                fig.update_layout(
                    xaxis_title="Subreddit",
                    yaxis_title="Number of Posts",
                    coloraxis_colorbar_title="Avg Score"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating subreddit distribution chart: {str(e)}")
    
        # Time Analysis
        with viz_tab3:
            try:
                if 'created_utc' in df.columns:
                    # Create a copy of the dataframe for time analysis
                    time_df = df.copy()
                    
                    # Handle different date formats with better error handling
                    time_df['created_date'] = pd.to_datetime(time_df['created_utc'], errors='coerce')
                    
                    # Filter out rows where date parsing failed
                    valid_dates = time_df['created_date'].notna()
                    invalid_dates_count = len(time_df) - valid_dates.sum()
                    
                    if valid_dates.sum() == 0:
                        st.warning("Could not parse any date formats. Please check the date formatting in your data.")
                        return
                    elif invalid_dates_count > 0:
                        st.warning(f"{invalid_dates_count} posts ({invalid_dates_count/len(time_df):.1%}) had invalid date formats and were excluded from time analysis.")
                    
                    time_df = time_df[valid_dates]
                    
                    # Create two columns for hour and day charts
                    time_col1, time_col2 = st.columns(2)
                    
                    with time_col1:
                        # Extract hour of day
                        time_df['hour_of_day'] = time_df['created_date'].dt.hour
                        
                        # Create the histogram with all hours (0-23) represented
                        hours_df = pd.DataFrame({'hour_of_day': range(24)})
                        hour_counts = time_df['hour_of_day'].value_counts().reset_index()
                        hour_counts.columns = ['hour', 'count']
                        hours_df = hours_df.merge(hour_counts, left_on='hour_of_day', right_on='hour', how='left').fillna(0)
                        
                        # Add hour labels with AM/PM for better readability
                        hours_df['hour_label'] = hours_df['hour_of_day'].apply(
                            lambda x: f"{x}:00" + (" AM" if x < 12 else " PM")
                        )
                        
                        fig = px.bar(hours_df, x='hour_of_day', y='count',
                                    title="Posts by Hour of Day (UTC)",
                                    color_discrete_sequence=['#1f77b4'])  # Use a standard blue color
                        
                        fig.update_layout(
                            xaxis_title="Hour of Day (UTC)",
                            yaxis_title="Number of Posts",
                            xaxis=dict(
                                tickmode='linear', 
                                tick0=0, 
                                dtick=2,  # Show every other hour for cleaner look
                                range=[-0.5, 23.5],  # Ensure all hours are shown
                                ticktext=[f"{h}" for h in range(0, 24, 2)],  # Custom labels
                                tickvals=list(range(0, 24, 2))
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with time_col2:
                        # Add a day of week visualization
                        time_df['day_of_week'] = time_df['created_date'].dt.day_name()
                        
                        # Make sure days are in correct order
                        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        day_counts = time_df['day_of_week'].value_counts().reindex(day_order).reset_index()
                        day_counts.columns = ['day', 'count']
                        
                        # Add day shortnames for better display
                        day_counts['day_short'] = day_counts['day'].apply(lambda x: x[:3])
                        
                        fig = px.bar(day_counts, x='day', y='count',
                                    title="Posts by Day of Week",
                                    color_discrete_sequence=['#2ca02c'])  # Use a standard green color
                        
                        fig.update_layout(
                            xaxis_title="Day of Week",
                            yaxis_title="Number of Posts",
                            xaxis=dict(
                                categoryorder='array',
                                categoryarray=day_order
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Add a date range histogram to show post distribution over time
                    st.subheader("Post Distribution Over Time")
                    
                    # Extract date only (no time) for grouping
                    time_df['post_date'] = time_df['created_date'].dt.date
                    
                    # Group by date and count posts
                    date_counts = time_df.groupby('post_date').size().reset_index(name='count')
                    date_counts['post_date'] = pd.to_datetime(date_counts['post_date'])
                    
                    # Plot the time series
                    fig = px.line(date_counts, x='post_date', y='count',
                                title="Post Volume Over Time",
                                markers=True)
                    
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Number of Posts"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No date information available for Time Analysis.")
            except Exception as e:
                st.error(f"Error creating time analysis charts: {str(e)}")
    except Exception as e:
        st.error(f"Error generating visualizations: {str(e)}")

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
    
    # Header using Streamlit's native heading components
    st.title("Reddit Scraper")
    st.header("Data Collection Tool")
    
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
                        
                        # Handle the case where there are no posts or only one post
                        if len(posts) == 0:
                            st.info(f"No posts found to display details.")
                        elif len(posts) == 1:
                            # For a single post, no need for a slider
                            post_index = 0
                            st.info(f"Displaying the only post found.")
                        else:
                            # For multiple posts, create a slider
                            post_index = st.slider(f"Select post from r/{subreddit} ({len(posts)} posts)", 
                                                  0, len(posts)-1, 0)
                        
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
            # Display loading state while generating visualizations
            with st.spinner("Generating visualizations..."):
                # Apply current filters to visualization data
                filtered_results = filter_results(st.session_state.results, st.session_state.filters)
                
                # Check if we have any results after filtering
                total_posts = sum(len(posts) for posts in filtered_results.values())
                if total_posts == 0:
                    st.warning("No posts match your current filters. Try adjusting your filter criteria.")
                else:
                    # Continue with visualization
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
