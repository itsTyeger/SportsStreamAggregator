# Sports URL Scraper

A Python application that extracts sports-related URLs from webpages and retrieves game schedules with accurate timing information.

## Features

- Extracts sports-related URLs from webpages
- Intelligently identifies and associates team matchups
- Retrieves game schedules from ESPN for all major sports leagues (NBA, NFL, MLB, NHL)
- Displays countdown timers for upcoming games
- Converts relative URLs to absolute URLs
- Handles errors gracefully
- Validates URLs before processing

## Recent Updates (v1.0.2)

- Fixed issue where LIVE games were not being displayed correctly on the UI
- Improved team name matching for Chicago teams in both backend and frontend
- Enhanced live game detection with better matching algorithms
- Cleaned up codebase and organized test scripts
- Added additional debug logging for easier troubleshooting

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Flask application:
```bash
python app.py
```
  or use the included batch file on Windows:
```
run_app.bat
```

2. Open a web browser and navigate to http://localhost:5000
3. Enter a URL containing sports content
4. Select the sport you're interested in
5. View the extracted URLs and game schedules

## Testing

The application includes a comprehensive suite of test scripts located in the `TestScripts` directory. 
For information on how to use these scripts, refer to the `README.md` file in the `TestScripts` directory.

## Project Structure

- `app.py` - Main application file containing the Flask server and scraping logic
- `templates/` - Contains HTML templates for the web interface
- `requirements.txt` - Python package dependencies
- `TestScripts/` - Test scripts for various components of the application
- `run_app.bat` - Convenience script for running the application on Windows

## Error Handling

The application handles various errors:
- Invalid URLs
- Network connection issues
- Timeout errors
- Invalid HTML content
- Date parsing issues
- Team name matching problems

## Note

Please be respectful of websites' robots.txt files and terms of service when scraping URLs. 