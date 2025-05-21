from urllib.parse import urlparse

def is_valid_url(url):
    """Validates if a given string is a properly formatted URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False 