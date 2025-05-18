# Test Scripts Directory

This directory contains test scripts for the Sports URL Scraper application. These scripts help verify different aspects of the application's functionality.

## Available Test Scripts

1. **test_duplicate_games.py** - Tests the prevention of duplicate games in game schedules
2. **test_game_times.py** - Tests the parsing and display of game times
3. **test_same_city_teams.py** - Tests handling of games with teams from the same city (e.g., Yankees vs Mets)
4. **test_same_city_teams_and_live.py** - Tests handling of same-city teams with live games
5. **test_team_codes.py** - Tests the parsing of team codes from ESPN URLs
6. **test_espn_dates.py** - Tests the date parsing from ESPN schedule pages
7. **test_scrape.py** - Tests the URL scraping functionality
8. **examine_espn.py** - Utility to examine the structure of ESPN pages
9. **url_scraper.py** - Tests the URL scraper function independently

## How to Run Test Scripts

### Basic Execution

To run any test script, use the Python interpreter:

```
python TestScripts/test_game_times.py
```

### Modifying Test Parameters

Most test scripts accept command-line arguments to customize their behavior. Here are some common parameters:

#### test_game_times.py
```
python TestScripts/test_game_times.py MLB
```
Replace `MLB` with any of the supported sports: `NBA`, `NFL`, `NHL`

#### test_same_city_teams.py
```
python TestScripts/test_same_city_teams.py --sport MLB --teams "Los Angeles" "New York"
```
Parameters:
- `--sport`: The sport to test (MLB, NBA, NFL, NHL)
- `--teams`: Cities with multiple teams to test

#### test_duplicate_games.py
```
python TestScripts/test_duplicate_games.py --sport MLB --output-file results.txt
```
Parameters:
- `--sport`: The sport to test
- `--output-file`: Where to save the results

#### test_scrape.py
```
python TestScripts/test_scrape.py --url "https://example.com/sports" --sport MLB
```
Parameters:
- `--url`: The URL to scrape
- `--sport`: The sport to use for game time lookup

## Creating Your Own Test Scripts

If you need to create additional test scripts, you can use the existing ones as templates. Make sure to:

1. Import the necessary modules from the main application
2. Set up appropriate test cases
3. Include clear output messages
4. Add command-line argument parsing for flexibility

## Helpful Tips

- Use the `--debug` flag (if supported by the script) for more detailed output
- Test scripts marked with `_and_live` specifically test handling of live games
- The HTML files in this directory are cached versions of ESPN schedules that can be used for testing without making network requests 