import praw
import pandas as pd
import datetime
import re
import json
import os
import os.path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

class EnhancedRedditScraper:
    """
    An enhanced Reddit scraper that provides more advanced functionality
    than the basic RedditScraperAgent.
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize the Reddit scraper with API credentials.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for Reddit API
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.last_search_results = []
        
    def scrape_subreddit(self, 
                         subreddit_name: str, 
                         keywords: List[str], 
                         limit: int = 100, 
                         sort_by: str = "hot",
                         include_comments: bool = False,
                         min_score: int = 0,
                         include_selftext: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape a subreddit for posts containing specified keywords.
        
        Args:
            subreddit_name: Name of the subreddit to scrape
            keywords: List of keywords to search for
            limit: Maximum number of posts to retrieve
            sort_by: How to sort posts ('hot', 'new', 'top', 'rising')
            include_comments: Whether to search post comments 
            min_score: Minimum score (upvotes) for posts
            include_selftext: Whether to search post content (selftext)
            
        Returns:
            List of matching post dictionaries
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        results = []
        
        # Choose the right sort method
        if sort_by == "hot":
            submissions = subreddit.hot(limit=limit)
        elif sort_by == "new":
            submissions = subreddit.new(limit=limit)
        elif sort_by == "top":
            submissions = subreddit.top(limit=limit)
        elif sort_by == "rising":
            submissions = subreddit.rising(limit=limit)
        else:
            submissions = subreddit.hot(limit=limit)
        
        # Process each submission
        for submission in submissions:
            # Check if post meets the minimum score requirement
            if submission.score < min_score:
                continue
                
            # Check for keywords in title or selftext
            title_match = any(keyword.lower() in submission.title.lower() for keyword in keywords)
            selftext_match = False
            
            if include_selftext:
                selftext_match = any(keyword.lower() in submission.selftext.lower() for keyword in keywords)
            
            comment_match = False
            comments_data = []
            
            # Search comments if enabled
            if include_comments:
                submission.comments.replace_more(limit=3)  # Load some MoreComments
                for comment in submission.comments.list()[:20]:  # Limit to first 20 comments
                    if any(keyword.lower() in comment.body.lower() for keyword in keywords):
                        comment_match = True
                        comments_data.append({
                            'author': str(comment.author),
                            'body': comment.body,
                            'score': comment.score,
                            'created_utc': datetime.datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                        })
            
            # Add post to results if it matches criteria
            if title_match or selftext_match or comment_match:
                created_time = datetime.datetime.fromtimestamp(submission.created_utc)
                
                post_data = {
                    'title': submission.title,
                    'text': submission.selftext,
                    'url': submission.url,
                    'score': submission.score,
                    'id': submission.id,
                    'author': str(submission.author),
                    'created_utc': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'permalink': f"https://www.reddit.com{submission.permalink}",
                }
                
                if include_comments and comments_data:
                    post_data['matching_comments'] = comments_data
                
                results.append(post_data)
        
        # Store last search results
        self.last_search_results = results
        return results
    
    def search_multiple_subreddits(self, 
                                  subreddits: List[str], 
                                  keywords: List[str], 
                                  **kwargs) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search multiple subreddits for the same keywords.
        
        Args:
            subreddits: List of subreddit names to search
            keywords: List of keywords to search for
            **kwargs: Additional arguments to pass to scrape_subreddit
            
        Returns:
            Dictionary mapping subreddit names to their results
        """
        results = {}
        for subreddit in subreddits:
            results[subreddit] = self.scrape_subreddit(subreddit, keywords, **kwargs)
        return results
    
    def save_results_to_csv(self, filename: str) -> str:
        """
        Save the last search results to a CSV file.
        
        Args:
            filename: Name of the file to save (without extension)
            
        Returns:
            Path to the saved file
        """
        if not self.last_search_results:
            raise ValueError("No search results to save. Run a search first.")
        
        df = pd.DataFrame(self.last_search_results)
        
        # Clean up comment data for CSV format
        if 'matching_comments' in df.columns:
            df['matching_comments'] = df['matching_comments'].apply(
                lambda x: json.dumps(x) if isinstance(x, list) else ''
            )
        
        # Add timestamp to filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.csv"
        
        df.to_csv(full_filename, index=False)
        return os.path.abspath(full_filename)
    
    def save_results_to_json(self, filename: str) -> str:
        """
        Save the last search results to a JSON file.
        
        Args:
            filename: Name of the file to save (without extension)
            
        Returns:
            Path to the saved file
        """
        if not self.last_search_results:
            raise ValueError("No search results to save. Run a search first.")
        
        # Add timestamp to filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.json"
        
        with open(full_filename, 'w', encoding='utf-8') as f:
            json.dump(self.last_search_results, f, ensure_ascii=False, indent=2)
        
        return os.path.abspath(full_filename)


# Example usage
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables or use defaults for development
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "RedditScraperApp/1.0")
    
    if not client_id or not client_secret:
        print("Warning: Reddit API credentials not found in environment variables.")
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env file")
        print("or as environment variables for proper functionality.")
        # For development only, you could set default credentials here
    
    # Create the scraper instance
    scraper = EnhancedRedditScraper(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    
    # Simple example
    try:
        results = scraper.scrape_subreddit(
            subreddit_name="cuny",
            keywords=["question", "help", "confused"],
            limit=25,
            sort_by="hot",
            include_comments=True
        )
        
        print(f"Found {len(results)} matching posts")
        
        # Save results to file
        if results:
            csv_path = scraper.save_results_to_csv("reddit_results")
            json_path = scraper.save_results_to_json("reddit_results")
            print(f"Results saved to {csv_path} and {json_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("This may be due to missing or invalid API credentials.")
