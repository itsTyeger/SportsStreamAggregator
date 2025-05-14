# URL Scraper

A simple Python application that extracts all URLs from a given webpage.

## Features

- Extracts all unique URLs from a webpage
- Converts relative URLs to absolute URLs
- Handles errors gracefully
- Supports command-line arguments or interactive input
- Validates URLs before processing

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

You can use the script in two ways:

1. Command-line argument:
```bash
python url_scraper.py https://example.com
```

2. Interactive mode:
```bash
python url_scraper.py
```
Then enter the URL when prompted.

## Output

The script will display:
- The URL being scraped
- The number of unique URLs found
- A numbered list of all URLs found

## Error Handling

The script handles various errors:
- Invalid URLs
- Network connection issues
- Timeout errors
- Invalid HTML content

## Note

Please be respectful of websites' robots.txt files and terms of service when scraping URLs. 