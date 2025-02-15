import feedparser
import datetime
import csv
from typing import List, Dict, Optional
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
                    
                parsed_entry = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:500],  # Limit summary length
                    'company': self._extract_company(entry),
                    'categories': ','.join([tag.term for tag in entry.get('tags', [])])
                }
                entries.append(parsed_entry)
                
                # Early exit if we've reached the limit
                if limit and len(entries) >= limit:
                    break
                    
        except Exception as e:
            print(f"Error processing entries: {str(e)}")
            
        return entries

    def _extract_company(self, entry: Dict) -> str:
        """
        Extract company name from entry metadata (optimized).
        
        Args:
            entry (Dict): Feed entry
            
        Returns:
            str: Extracted company name or empty string
        """
        # Quick checks for common company information locations
        if hasattr(entry, 'source') and entry.source.get('title'):
            return entry.source.get('title', '')
        
        if hasattr(entry, 'author'):
            return entry.author
            
        # Only check content if other methods fail
        if hasattr(entry, 'content'):
            try:
                first_line = entry.content[0].value.split('\n')[0]
                if ' - ' in first_line:
                    return first_line.split(' - ')[0].strip()
            except (IndexError, AttributeError):
                pass
                
        return ''


def main(num_articles: int, timeout: int):
    # Example usage with performance monitoring
    feed_urls = [
        # 'https://www.prnewswire.com/rss/news-releases-list.rss',
        'https://www.prnewswire.com/rss/telecommunications-latest-news/telecommunications-latest-news-list.rss'
    ]
    
    # Dictionary to store results
    results = {}
    
    for url in feed_urls:
        start_time = time.time()
        parser = PRWireParser(url, timeout=timeout)  # 10 second timeout
        
        if parser.fetch_feed():
            # Get latest entry
            entries = parser.get_entries(limit=num_articles)
            
            if entries:
                # Store entries in dictionary with timestamp as key
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                results[timestamp] = entries[0]  # Store the single entry
                
                print(f"Stored entry from {url} in results dictionary")
                print(f"Total processing time: {time.time() - start_time:.2f} seconds")
            else:
                print(f"No valid entries found for {url}")
        else:
            print(f"Failed to fetch feed from {url}")

    print(results)
    
    return results  # Return the dictionary containing all entries

if __name__ == "__main__":
    num_articles = 3
    timeout = 10
    main(num_articles, timeout)