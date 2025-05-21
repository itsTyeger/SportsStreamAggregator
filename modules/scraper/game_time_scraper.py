import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone, timedelta
import pytz
from ..utils.team_utils import get_official_team_name, get_all_teams_for_sport
from .game_processors import process_game_row

def get_game_times(sport):
    """Fetches game times from ESPN's schedule for specified sport."""
    try:
        # Map sport to ESPN URL
        sport_urls = {
            'NBA': 'https://www.espn.com/nba/schedule',
            'NFL': 'https://www.espn.com/nfl/schedule',
            'MLB': 'https://www.espn.com/mlb/schedule',
            'NHL': 'https://www.espn.com/nhl/schedule'
        }
        
        if sport not in sport_urls:
            print(f"Unsupported sport: {sport}")
            return {}
            
        url = sport_urls[sport]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"Fetching schedule from {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # If MLB, look for specific data sections including the "RESULT" column
        if sport == 'MLB':
            # Check if the page has a RESULT section which indicates completed games
            result_sections = soup.find_all('div', string=lambda s: s and 'RESULT' in s)
            if result_sections:
                print(f"Found RESULT sections: {len(result_sections)}")
            
            # Look for MATCHUP/RESULT headers
            matchup_headers = soup.find_all(['th', 'div'], string=lambda s: s and 'MATCHUP' in s)
            result_headers = soup.find_all(['th', 'div'], string=lambda s: s and 'RESULT' in s)
            print(f"Found MATCHUP headers: {len(matchup_headers)}")
            print(f"Found RESULT headers: {len(result_headers)}")
            
            # Check for table structure at a high level
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")
            
            # Examine each table to see if it might contain results
            for i, table in enumerate(tables):
                headers = table.find_all('th')
                header_texts = [h.text.strip() for h in headers]
                print(f"Table {i} headers: {header_texts}")
                
                # Check each row for POSTPONED games
                rows = table.find_all('tr')
                for row in rows:
                    row_text = row.text.strip().upper()
                    if "POSTPONED" in row_text:
                        print(f"Found POSTPONED in row: {row_text[:50]}...")
        
        game_times = {}
        
        # Track which teams are already scheduled to prevent duplicates
        teams_with_games_today = set()
        
        # Track unique game IDs to prevent duplicates across sections
        processed_game_ids = set()
        
        # Get today's date
        today_date = datetime.now().strftime('%Y-%m-%d')
        today = datetime.now().date()
        print(f"Current date: {today_date}")
        
        # Find all date headers - can be either h2 or div with class Table__Title
        date_headers = soup.find_all(['h2', 'div'], class_='Table__Title')
        print(f"Found {len(date_headers)} date headers:")
        
        # Maps to store date headers and their associated table elements
        date_to_tables = {}
        
        # First pass: find all date headers and associated tables
        for header in date_headers:
            date_text = header.text.strip()
            try:
                # ESPN date format is like: "Sunday, May 19, 2024"
                parsed_date = datetime.strptime(date_text, '%A, %B %d, %Y')
                print(f"Found date header: {parsed_date.strftime('%Y-%m-%d')} - {date_text}")
                
                # Find the parent ScheduleTables container
                schedule_table = header.find_parent(class_=lambda c: c and 'ScheduleTables' in c)
                
                # If no direct parent found, look for the next sibling that contains the table
                if not schedule_table:
                    schedule_table = header.find_next_sibling()
                
                # Find the ResponsiveTable in this section
                responsive_table = None
                if schedule_table:
                    responsive_table = schedule_table.find('div', class_='ResponsiveTable')
                
                # If no table found yet, try another approach - find the next ResponsiveTable
                if not responsive_table:
                    responsive_table = header.find_next('div', class_='ResponsiveTable')
                
                if responsive_table:
                    if parsed_date not in date_to_tables:
                        date_to_tables[parsed_date] = []
                    date_to_tables[parsed_date].append(responsive_table)
                    print(f"Added table to date {parsed_date.strftime('%Y-%m-%d')}")
            except ValueError:
                print(f"Invalid date format: {date_text}")
        
        # Debug: Print all dates and their table counts
        print(f"Dates found with tables:")
        for date, tables in date_to_tables.items():
            print(f"  Date: {date.strftime('%Y-%m-%d')} - Tables: {len(tables)}")
            print(f"  Is today: {date.date() == today}")
        
        # If no date headers found or no tables for any date, fall back to all tables
        if not date_to_tables:
            print("No date sections found, using all tables as fallback with today's date")
            all_tables = soup.find_all('div', class_='ResponsiveTable')
            fallback_date = datetime.now()
            date_to_tables[fallback_date] = all_tables
            
            # Also try to find any tables with result columns
            result_tables = []
            tables = soup.find_all('table')
            for table in tables:
                headers = table.find_all('th')
                for header in headers:
                    if header.text.strip().upper() == "RESULT":
                        result_tables.append(table)
                        print(f"Found a table with RESULT header")
                        break
            
            if result_tables:
                fallback_date_result = datetime.now()
                date_to_tables[fallback_date_result] = result_tables
        
        # Track games processed
        processed_games = 0
        game_id = 0
        
        # Get date range: look at recent dates for completed games and upcoming dates for future games
        # We'll look at dates from 7 days ago to 2 days in the future
        date_range_start = today - timedelta(days=7)
        date_range_end = today + timedelta(days=2)
        
        # Additional MLB-specific section to look for completed games with postponed results
        if sport == 'MLB':
            # Look for the "MATCHUP" and "RESULT" sections which usually contain completed games
            matchup_result_sections = []
            
            # Try to find tables with both MATCHUP and RESULT headers
            for table in soup.find_all('table'):
                headers = [h.text.strip().upper() for h in table.find_all('th')]
                if 'MATCHUP' in headers and 'RESULT' in headers:
                    matchup_result_sections.append(table)
                    print(f"Found table with MATCHUP and RESULT headers: {headers}")
            
            # Process each table with result information
            for table_idx, table in enumerate(matchup_result_sections):
                # Get all rows from the table
                rows = table.find_all('tr')
                
                # Skip header row
                for row_idx, row in enumerate(rows[1:], start=1):
                    try:
                        processed_games += 1
                        game_id += 1
                        
                        # Extract all cells from the row
                        cells = row.find_all('td')
                        
                        # Check if this is likely a POSTPONED game
                        row_text = row.text.strip().upper()
                        is_postponed = "POSTPONED" in row_text
                        
                        if is_postponed:
                            print(f"Processing likely POSTPONED game in results section, row {row_idx}")
                        
                        # Process this game row and add to game_times if valid
                        game_times = process_game_row(
                            sport,
                            row, 
                            cells, 
                            game_id, 
                            row_idx, 
                            table_idx,
                            today,  # Use today as the section date for result sections
                            teams_with_games_today,
                            processed_game_ids,
                            game_times
                        )
                    except Exception as e:
                        print(f"Error parsing game row in results section: {e}")
                        continue
        
        # Process each date and its tables
        for section_date, tables in date_to_tables.items():
            section_date_obj = section_date.date()
            section_is_today = section_date_obj == today
            
            # Check if this date is within our processing range
            date_in_range = date_range_start <= section_date_obj <= date_range_end
            
            print(f"Processing section for date: {section_date.strftime('%Y-%m-%d')} (is_today: {section_is_today}, in_range: {date_in_range})")
            
            # Only process games for dates within our range
            if not date_in_range:
                print(f"Skipping section for {section_date.strftime('%Y-%m-%d')} as it's outside our date range")
                continue
            
            # For dates before today, we're primarily interested in completed games
            is_past_date = section_date_obj < today
            if is_past_date:
                print(f"Processing past date {section_date.strftime('%Y-%m-%d')} for completed games")
            
            # Process each table for this date
            for table_idx, table in enumerate(tables):
                # Get all game rows
                game_rows = table.find_all('tr', class_=lambda x: x and 'Table__TR' in x)
                
                # If no rows found with that class, try any tr
                if not game_rows:
                    game_rows = table.find_all('tr')
                    print(f"No rows with Table__TR class, found {len(game_rows)} regular tr elements")
                
                # Track position in each row
                row_position = 0
                
                for row in game_rows:
                    try:
                        # Skip header rows
                        if row.find('th'):
                            continue
                            
                        processed_games += 1
                        row_position += 1
                        game_id += 1
                        
                        # Extract all cells from the row
                        team_cells = row.find_all('td', class_='Table__TD')
                        
                        # If no cells with that class, try any td
                        if len(team_cells) < 2:
                            team_cells = row.find_all('td')
                            print(f"Found {len(team_cells)} regular td elements")
                            
                        if len(team_cells) < 2:
                            continue
                        
                        # Process this game row and add to game_times if valid
                        game_times = process_game_row(
                            sport,
                            row, 
                            team_cells, 
                            game_id, 
                            row_position, 
                            table_idx,
                            section_date,
                            teams_with_games_today,
                            processed_game_ids,
                            game_times
                        )
                    except Exception as e:
                        print(f"Error parsing game row: {e}")
                        print(f"--- SKIPPED PROCESSING: General processing error ---\n")
                        continue
        
        # Add a timestamp indicating when the game times were fetched
        game_times['_meta'] = {
            'date': today_date,
            'timestamp': datetime.now().isoformat(),
            'game_count': len(game_times) - (2 if 'team_games' in game_times and '_meta' in game_times else 1 if 'team_games' in game_times or '_meta' in game_times else 0)
        }
        
        print(f"Processed {processed_games} rows, found {len(game_times) - 2 if 'team_games' in game_times and '_meta' in game_times else len(game_times) - 1 if 'team_games' in game_times or '_meta' in game_times else len(game_times)} game times for {sport} on {today_date}")
        return game_times
    except Exception as e:
        print(f"Error fetching {sport} schedule: {e}")
        return {} 