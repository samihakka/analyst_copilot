import feedparser
import datetime
import csv
from typing import List, Dict, Optional  # Added Optional here
import requests
from requests.exceptions import RequestException
import socket
import time
class PRWireParser:
    def __init__(self, feed_url: str, timeout: int = 10):
        """
        Initialize the PR Wire parser with a feed URL.
        
        Args:
            feed_url (str): The URL of the RSS feed to parse
            timeout (int): Timeout in seconds for feed requests
        """
        self.feed_url = feed_url
        self.timeout = timeout
        self.feed_data = None
        
        # Set socket timeout globally
        socket.setdefaulttimeout(timeout)

    def fetch_feed(self) -> bool:
        """
        Fetch and parse the RSS feed with timeout handling.
        
        Returns:
            bool: True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            # First get the raw feed content with timeout
            response = requests.get(self.feed_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse the feed content
            self.feed_data = feedparser.parse(response.content)
            
            # Check if parsing was successful
            if not hasattr(self.feed_data, 'entries'):
                print(f"No entries found in feed: {self.feed_url}")
                return False
                
            print(f"Feed fetched in {time.time() - start_time:.2f} seconds")
            return len(self.feed_data.entries) > 0
            
        except RequestException as e:
            print(f"Request error fetching feed {self.feed_url}: {str(e)}")
            return False
        except Exception as e:
            print(f"Error parsing feed {self.feed_url}: {str(e)}")
            return False

    def get_entries(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get parsed entries from the feed with performance optimization.
        
        Args:
            limit (Optional[int]): Maximum number of entries to return
            
        Returns:
            List[Dict]: List of parsed entries
        """
        if not self.feed_data:
            if not self.fetch_feed():
                return []

        entries = []
        try:
            # Limit the number of entries to process
            feed_entries = self.feed_data.entries[:limit] if limit else self.feed_data.entries
            
            for entry in feed_entries:
                # Skip entries that don't have required fields
                if not entry.get('title') or not entry.get('link'):
                    continue
                    
                # Get the full content
                content = self._extract_full_content(entry)
                
                parsed_entry = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'content': content,
                    'author': entry.get('author', ''),
                    'categories': self._extract_categories(entry)
                }
                entries.append(parsed_entry)
                
                # Early exit if we've reached the limit
                if limit and len(entries) >= limit:
                    break
                    
        except Exception as e:
            print(f"Error processing entries: {str(e)}")
            
        return entries

    def _extract_full_content(self, entry: Dict) -> str:
        """
        Extract full content from entry, trying multiple possible locations.
        
        Args:
            entry (Dict): Feed entry
            
        Returns:
            str: Full content or empty string
        """
        # Try content field first
        if hasattr(entry, 'content'):
            try:
                return entry.content[0].value
            except (IndexError, AttributeError):
                pass
        
        # Try content:encoded field
        if hasattr(entry, 'content_encoded'):
            return entry.content_encoded
            
        # Try description field
        if hasattr(entry, 'description'):
            return entry.description
            
        # Fall back to summary if nothing else is available
        return entry.get('summary', '')

    def _extract_categories(self, entry: Dict) -> str:
        """
        Extract categories from entry.
        
        Args:
            entry (Dict): Feed entry
            
        Returns:
            str: Comma-separated categories
        """
        if hasattr(entry, 'tags'):
            return ','.join([tag.term for tag in entry.tags])
        elif hasattr(entry, 'categories'):
            return ','.join(entry.categories)
        return ''
    
def main(num_articles: int, timeout: int):
    feed_url = 'https://www.lux.camera/rss/'
    parser = PRWireParser(feed_url, timeout=timeout)
    
    if parser.fetch_feed():
        entries = parser.get_entries(limit=num_articles)
        for entry in entries:
            print(f"\nTitle: {entry['title']}")
            print(f"Author: {entry['author']}")
            print(f"Published: {entry['published']}")
            print(f"Categories: {entry['categories']}")
            # print(f"Content length: {len(entry['content'])} characters")
            print("\nContent:")
            print("-" * 80)
            print(entry['content'])
            print("-" * 80)
            print("Content preview:", entry['content'])
            print("-" * 80)
    
    return entries

if __name__ == "__main__":
    entries = main(num_articles=1, timeout=10)