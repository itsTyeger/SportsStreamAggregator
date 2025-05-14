# Import required libraries
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML content
import sys  # For accessing command line arguments
from urllib.parse import urljoin, urlparse  # For URL manipulation and validation
import re

def is_valid_url(url):
    """
    Validates if a given string is a properly formatted URL.
    
    Args:
        url (str): The URL string to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
        
    Example:
        >>> is_valid_url("https://example.com")
        True
        >>> is_valid_url("not-a-url")
        False
    """
    try:
        # Parse the URL into its components
        result = urlparse(url)
        # Check if the URL has both a scheme (http/https) and a network location (domain)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_all_urls(url):
    """
    Extracts all unique URLs from a given webpage that contain 'nba/<cityname>' in the path.
    
    Args:
        url (str): The URL of the webpage to scrape
        
    Returns:
        list: A sorted list of unique absolute URLs found on the page that contain 'nba/<cityname>'
        
    The function:
    1. Makes an HTTP GET request to the URL
    2. Parses the HTML content
    3. Finds all anchor tags with href attributes
    4. Converts relative URLs to absolute URLs
    5. Filters out invalid URLs and URLs that don't contain 'nba/<cityname>'
    6. Returns a sorted list of unique URLs
    """
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Send a GET request to the URL with headers
        response = requests.get(url, headers=headers, timeout=10)
        # Raise an exception for bad status codes (4xx, 5xx)
        response.raise_for_status()
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize a set to store unique URLs
        urls = set()
        
        # Regex: nba/<cityname> (cityname = letters or hyphens, not followed by another slash immediately)
        pattern = re.compile(r"/nba/([a-zA-Z\-]+)(/|$)")
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(url, href)
            if is_valid_url(absolute_url):
                # Check if the pattern exists in the path
                match = pattern.search(absolute_url)
                if match:
                    urls.add(absolute_url)
        
        # Convert set to sorted list and return
        return sorted(list(urls))
    
    except requests.RequestException as e:
        # Handle network-related errors (connection issues, timeouts, etc.)
        print(f"Error fetching the URL: {e}")
        return []
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An error occurred: {e}")
        return []

def main():
    """
    Main function that handles user input and displays results.
    """
    print("\n" + "="*50)
    print("URL SCRAPER - NBA LINKS")
    print("="*50 + "\n")
    
    default_url = "https://the.streameast.app/v87"
    url = None

    # Get URL from command line argument or user input
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        try:
            print(f"Press Enter to use the default URL or paste your own.")
            print(f"URL [{default_url}]: ", end='', flush=True)
            user_input = input()
            url = user_input.strip() if user_input.strip() else default_url
        except Exception:
            url = default_url
    
    # Validate the URL before proceeding
    if not is_valid_url(url):
        print(f"\nInvalid URL provided. Please enter a valid URL (e.g., https://example.com)")
        return
    
    # Display the URL being scraped
    print(f"\nScraping URLs from: {url}")
    print("-" * 50)
    
    # Get all URLs from the webpage
    urls = get_all_urls(url)
    
    # Display results
    if urls:
        print(f"\nFound {len(urls)} unique URLs containing 'nba/':")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
    else:
        print("No URLs containing 'nba/' found or an error occurred.")
    
    print("\n" + "="*50 + "\n")

# Entry point of the script
if __name__ == "__main__":
    main() 