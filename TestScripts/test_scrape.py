import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz

def check_espn_schedules():
    """Test scraping of ESPN schedule pages to troubleshoot timing issues."""
    sports = {
        'NBA': 'https://www.espn.com/nba/schedule',
        'NFL': 'https://www.espn.com/nfl/schedule',
        'MLB': 'https://www.espn.com/mlb/schedule',
        'NHL': 'https://www.espn.com/nhl/schedule'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for sport, url in sports.items():
        print(f"\n===== Checking {sport} schedule at {url} =====")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find date container
            date_container = soup.find('h2', class_='Table__Title')
            date_text = date_container.text.strip() if date_container else "No date found"
            print(f"Schedule date: {date_text}")
            
            # Find all game tables
            game_tables = soup.find_all('div', class_='ResponsiveTable')
            print(f"Found {len(game_tables)} game tables")
            
            total_games = 0
            games_with_times = 0
            
            for table_idx, table in enumerate(game_tables):
                # Get all game rows
                game_rows = table.find_all('tr', class_=lambda x: x and 'Table__TR' in x)
                print(f"Table {table_idx + 1}: Found {len(game_rows)} game rows")
                
                for row_idx, row in enumerate(game_rows):
                    if row.find('th'):  # Skip header rows
                        continue
                    
                    total_games += 1
                    
                    # Get team cells
                    team_cells = row.find_all('td', class_='Table__TD')
                    
                    # Try to find teams and time
                    teams_text = []
                    time_text = "Not found"
                    
                    # Look for teams in various formats
                    team_links = row.find_all('a', class_='AnchorLink')
                    if len(team_links) >= 2:
                        teams_text = [team.text.strip() for team in team_links[:2]]
                    
                    # Look for time in various cells
                    for cell in team_cells:
                        cell_text = cell.text.strip()
                        if ':' in cell_text or 'LIVE' in cell_text or 'PM' in cell_text or 'AM' in cell_text:
                            time_text = cell_text
                            if not any(status in time_text for status in ['TBD', 'Postponed', 'PPD', 'FINAL']):
                                games_with_times += 1
                            break
                    
                    teams_str = " vs ".join(teams_text) if teams_text else "Teams not found"
                    print(f"  Game {row_idx + 1}: {teams_str} - Time: {time_text}")
            
            print(f"Summary for {sport}: {total_games} total games, {games_with_times} with valid times")
            
        except Exception as e:
            print(f"Error processing {sport} schedule: {str(e)}")

if __name__ == "__main__":
    check_espn_schedules() 