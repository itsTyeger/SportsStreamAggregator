# Sports Event Web Scraper Application Documentation

This document provides an overview of the application architecture, explaining the purpose and functionality of each component.

## Application Structure

The application follows a modular structure with clear separation of concerns:

```
testApp/
│
├── app.py                          # Main application entry point
├── run_app.bat                     # Batch file to run the application
├── requirements.txt                # Python dependencies
│
├── modules/                        # Main modules directory
│   ├── __init__.py                 # Package initializer
│   │
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py             # Exposes utility functions
│   │   ├── url_validator.py        # URL validation functionality
│   │   └── team_utils.py           # Team name processing utilities
│   │
│   ├── scraper/                    # Web scraping functionality
│   │   ├── __init__.py             # Exposes scraper functions
│   │   ├── url_scraper.py          # URL extraction from web pages
│   │   ├── game_time_scraper.py    # Game schedule scraping
│   │   │
│   │   └── game_processors/        # Game data processing
│   │       ├── __init__.py         # Exposes processor functions
│   │       ├── game_row_processor.py    # Processes a single game row
│   │       ├── live_game_processor.py   # Processes live games
│   │       ├── completed_game_processor.py # Processes completed games
│   │       └── upcoming_game_processor.py  # Processes upcoming games
│   │
│   └── routes/                     # Web routes
│       ├── __init__.py             # Package initializer
│       └── main_routes.py          # Main application routes
│
└── templates/                      # HTML templates for the web interface
```

## Component Details

### Main Application Files

- **app.py**: The entry point of the application. Initializes the Flask app and configures the routes.
- **run_app.bat**: A batch file to run the application on Windows systems.
- **requirements.txt**: Lists all Python package dependencies needed for the application.

### Modules

#### Utils Module

- **url_validator.py**: Contains the `is_valid_url()` function that validates whether a given string is a properly formatted URL.
- **team_utils.py**: Provides utilities for handling sports team names, including:
  - `SPORTS_TEAMS`: Dictionary of teams by sport
  - `ESPN_ABBREVIATIONS`: Dictionary of team abbreviations used by ESPN
  - `get_official_team_name()`: Matches input team names to official team names
  - `get_all_teams_for_sport()`: Returns all teams for a given sport

#### Scraper Module

- **url_scraper.py**: Contains the `get_all_urls()` function that extracts URLs from a webpage and identifies sports matches in them.
- **game_time_scraper.py**: Contains the `get_game_times()` function that scrapes game schedules from ESPN.

##### Game Processors

- **game_row_processor.py**: Contains the `process_game_row()` function that parses a single row of game data from ESPN tables. It extracts team names, game time, and other relevant information.
- **live_game_processor.py**: Contains the `process_live_game()` function that handles games currently in progress.
- **completed_game_processor.py**: Contains the `process_completed_game()` function that processes games that have already finished.
- **upcoming_game_processor.py**: Contains the `process_upcoming_game()` function that processes games scheduled for the future.

#### Routes Module

- **main_routes.py**: Defines the web routes for the application, including:
  - `/`: The home route that renders the main page
  - `/scrape`: The endpoint for scraping URLs from a provided website
  - `/debug_times/<sport>`: A debugging endpoint for viewing game times for a specific sport

### Templates

- Contains HTML templates for the web interface.

## Data Flow

1. The user accesses the application through their browser, which loads the home page.
2. The user enters a URL and selects a sport to scrape.
3. The application validates the URL and then:
   - Uses `get_all_urls()` to extract sports-related URLs from the provided webpage
   - Uses `get_game_times()` to fetch current game schedules from ESPN for the selected sport
4. The results are returned to the user's browser, which displays the extracted URLs and game times.

## Key Functionalities

1. **URL Validation**: Ensures that only properly formatted URLs are processed.
2. **Team Name Matching**: Sophisticated matching of team names to handle variations and abbreviations.
3. **Sports Event URL Extraction**: Identifies URLs that likely point to sports events by looking for patterns of team names.
4. **Game Schedule Scraping**: Extracts current game schedules from ESPN, including:
   - Live games currently in progress
   - Completed games with results
   - Upcoming games with scheduled times
5. **Web Interface**: Provides a user-friendly interface for accessing these features.

## Dependencies

The application relies on the following Python packages:
- Flask: Web framework
- Requests: HTTP library for making requests
- BeautifulSoup4: HTML parsing library
- PyTZ: Timezone handling library 