from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime, timezone
import pytz

app = Flask(__name__)

def is_valid_url(url):
    """Validates if a given string is a properly formatted URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_all_urls(url):
    """Extracts all unique URLs from a given webpage and attempts to identify sports teams in them."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = set()
        
        # Dictionary of sports and their teams
        sports_teams = {
            'NBA': {
                'Boston Celtics', 'Brooklyn Nets', 'New York Knicks', 'Philadelphia 76ers', 'Toronto Raptors',
                'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers', 'Milwaukee Bucks',
                'Atlanta Hawks', 'Charlotte Hornets', 'Miami Heat', 'Orlando Magic', 'Washington Wizards',
                'Denver Nuggets', 'Minnesota Timberwolves', 'Oklahoma City Thunder', 'Portland Trail Blazers', 'Utah Jazz',
                'Golden State Warriors', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Phoenix Suns', 'Sacramento Kings',
                'Dallas Mavericks', 'Houston Rockets', 'Memphis Grizzlies', 'New Orleans Pelicans', 'San Antonio Spurs'
            },
            'NFL': {
                'Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills', 'Carolina Panthers',
                'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns', 'Dallas Cowboys', 'Denver Broncos',
                'Detroit Lions', 'Green Bay Packers', 'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars',
                'Kansas City Chiefs', 'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
                'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants', 'New York Jets',
                'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers', 'Seattle Seahawks', 'Tampa Bay Buccaneers',
                'Tennessee Titans', 'Washington Commanders'
            },
            'MLB': {
                'Arizona Diamondbacks', 'Atlanta Braves', 'Baltimore Orioles', 'Boston Red Sox', 'Chicago Cubs',
                'Chicago White Sox', 'Cincinnati Reds', 'Cleveland Guardians', 'Colorado Rockies', 'Detroit Tigers',
                'Houston Astros', 'Kansas City Royals', 'Los Angeles Angels', 'Los Angeles Dodgers', 'Miami Marlins',
                'Milwaukee Brewers', 'Minnesota Twins', 'New York Mets', 'New York Yankees', 'Oakland Athletics',
                'Philadelphia Phillies', 'Pittsburgh Pirates', 'San Diego Padres', 'San Francisco Giants', 'Seattle Mariners',
                'St. Louis Cardinals', 'Tampa Bay Rays', 'Texas Rangers', 'Toronto Blue Jays', 'Washington Nationals'
            },
            'NHL': {
                'Anaheim Ducks', 'Arizona Coyotes', 'Boston Bruins', 'Buffalo Sabres', 'Calgary Flames',
                'Carolina Hurricanes', 'Chicago Blackhawks', 'Colorado Avalanche', 'Columbus Blue Jackets', 'Dallas Stars',
                'Detroit Red Wings', 'Edmonton Oilers', 'Florida Panthers', 'Los Angeles Kings', 'Minnesota Wild',
                'Montreal Canadiens', 'Nashville Predators', 'New Jersey Devils', 'New York Islanders', 'New York Rangers',
                'Ottawa Senators', 'Philadelphia Flyers', 'Pittsburgh Penguins', 'San Jose Sharks', 'Seattle Kraken',
                'St. Louis Blues', 'Tampa Bay Lightning', 'Toronto Maple Leafs', 'Vancouver Canucks', 'Vegas Golden Knights',
                'Washington Capitals', 'Winnipeg Jets'
            }
        }

        # Create a dictionary of team variations for each sport
        team_variations_by_sport = {}
        for sport, teams in sports_teams.items():
            team_variations_by_sport[sport] = {}
            for team in teams:
                # Split into parts and get city and nickname
                parts = team.split()
                if len(parts) >= 2:
                    city = parts[0].lower()
                    nickname = ' '.join(parts[1:]).lower()
                    full_name = team.lower()
                    
                    # Add to sport-specific variations
                    team_variations_by_sport[sport][full_name] = team
                    team_variations_by_sport[sport][nickname] = team
                    
                    # Only add city if it's unique to this sport
                    is_city_unique = True
                    for other_sport, other_teams in sports_teams.items():
                        if other_sport != sport:
                            for other_team in other_teams:
                                other_parts = other_team.split()
                                if other_parts and other_parts[0].lower() == city:
                                    is_city_unique = False
                                    break
                        if not is_city_unique:
                            break
                            
                    # Only add city as a variation if it's unique to this sport
                    if is_city_unique:
                        team_variations_by_sport[sport][city] = team

        # Process all list items and links
        for element in soup.find_all(['li', 'a']):
            text = element.get_text().strip()
            href = element.get('href', '')
            
            # Skip empty elements
            if not text and not href:
                continue
                
            # Make URL absolute
            if href:
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = urljoin(url, href)
                if not href.startswith(('http://', 'https://')):
                    continue
            
            # Combine text for searching, converted to lowercase
            search_text = (text + ' ' + href).lower()
            
            # Find teams in the text for each sport separately
            for sport, variations in team_variations_by_sport.items():
                found_teams = set()
                
                # Match teams in this sport only
                for variation, team in variations.items():
                    # Check if the team name appears as a whole word
                    # Use word boundaries or space checks to ensure we're matching whole words
                    pattern = r'\b' + re.escape(variation) + r'\b'
                    if re.search(pattern, search_text):
                        found_teams.add(team)
                
                # Only process if we found at least two teams from the same sport
                if len(found_teams) >= 2:
                    # Take the first two teams found
                    teams_list = sorted(list(found_teams))[:2]
                    title = f"{sport}: {teams_list[0]} vs {teams_list[1]}"
                    if href:
                        urls.add((href, title))
                    else:
                        # If no href, use the parent link if available
                        parent_link = element.find_parent('a')
                        if parent_link and parent_link.get('href'):
                            parent_href = parent_link['href']
                            if parent_href.startswith('//'):
                                parent_href = 'https:' + parent_href
                            elif parent_href.startswith('/'):
                                parent_href = urljoin(url, parent_href)
                            if parent_href.startswith(('http://', 'https://')):
                                urls.add((parent_href, title))
        
        return sorted(list(urls))
    except requests.RequestException as e:
        return {"error": f"Error fetching the URL: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

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
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        game_times = {}
        
        # Track which teams are already scheduled for today to prevent duplicates
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
        
        # Track games processed
        processed_games = 0
        game_id = 0
        
        # Process each date and its tables
        for section_date, tables in date_to_tables.items():
            section_is_today = section_date.date() == today
            
            print(f"Processing section for date: {section_date.strftime('%Y-%m-%d')} (is_today: {section_is_today})")
            
            # Only process games for today's date
            if not section_is_today:
                print(f"Skipping section for {section_date.strftime('%Y-%m-%d')} as it's not today")
                continue
            
            # Process each table for this date
            for table_idx, table in enumerate(tables):
                # Get all game rows
                game_rows = table.find_all('tr', class_=lambda x: x and 'Table__TR' in x)
                
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
                        if len(team_cells) < 2:
                            continue
                        
                        # Try multiple approaches to find teams
                        team1 = None
                        team2 = None
                        
                        # First attempt - find all team links across all cells
                        all_team_links = row.find_all('a', class_='AnchorLink')
                        team_links = [link for link in all_team_links if link.find('abbr') or '/team/' in link.get('href', '') or 'gamecast' not in link.get('href', '')]
                        
                        if len(team_links) >= 2:
                            # Extract more detailed team info from href if possible
                            team1 = team_links[0].text.strip()
                            team2 = team_links[1].text.strip()
                            
                            # Check if we have links with team codes (particularly useful for same-city teams)
                            href1 = team_links[0].get('href', '')
                            href2 = team_links[1].get('href', '')
                            
                            # Extract team codes from hrefs (e.g. "laa" from "/mlb/team/_/name/laa/los-angeles-angels")
                            team1_code = None
                            team2_code = None
                            
                            if '/team/' in href1 and '/name/' in href1:
                                parts = href1.split('/name/')
                                if len(parts) > 1:
                                    code_parts = parts[1].split('/')
                                    if len(code_parts) > 0:
                                        team1_code = code_parts[0]
                            
                            if '/team/' in href2 and '/name/' in href2:
                                parts = href2.split('/name/')
                                if len(parts) > 1:
                                    code_parts = parts[1].split('/')
                                    if len(code_parts) > 0:
                                        team2_code = code_parts[0]
                            
                            # Special handling for Los Angeles teams using team codes
                            if team1 == 'Los Angeles' and team2 == 'Los Angeles' and team1_code and team2_code:
                                if team1_code.lower() == 'laa' and team2_code.lower() == 'lad':
                                    team1 = 'Los Angeles Angels'
                                    team2 = 'Los Angeles Dodgers'
                                    print(f"Fixed LA teams using codes: {team1} vs {team2}")
                                elif team1_code.lower() == 'lad' and team2_code.lower() == 'laa':
                                    team1 = 'Los Angeles Dodgers'
                                    team2 = 'Los Angeles Angels'
                                    print(f"Fixed LA teams using codes: {team1} vs {team2}")
                                    
                            # Special handling for New York teams using team codes
                            if team1 == 'New York' and team2 == 'New York' and team1_code and team2_code:
                                if team1_code.lower() == 'nym' and team2_code.lower() == 'nyy':
                                    team1 = 'New York Mets'
                                    team2 = 'New York Yankees'
                                    print(f"Fixed NY teams using codes: {team1} vs {team2}")
                                elif team1_code.lower() == 'nyy' and team2_code.lower() == 'nym':
                                    team1 = 'New York Yankees'
                                    team2 = 'New York Mets'
                                    print(f"Fixed NY teams using codes: {team1} vs {team2}")
                                    
                            # Special handling for Chicago teams using team codes
                            if team1 == 'Chicago' and team2 == 'Chicago' and team1_code and team2_code:
                                print(f"Differentiating Chicago teams with codes: {team1_code} vs {team2_code}")
                                if (team1_code.lower() == 'chc' or team1_code.lower() == 'chi') and (team2_code.lower() == 'chw' or team2_code.lower() == 'cws'):
                                    team1 = 'Chicago Cubs'
                                    team2 = 'Chicago White Sox'
                                    print(f"Fixed Chicago teams using codes: {team1} vs {team2}")
                                elif (team1_code.lower() == 'chw' or team1_code.lower() == 'cws') and (team2_code.lower() == 'chc' or team2_code.lower() == 'chi'):
                                    team1 = 'Chicago White Sox'
                                    team2 = 'Chicago Cubs'
                                    print(f"Fixed Chicago teams using codes: {team1} vs {team2}")
                        
                        # Second attempt - look for team name spans
                        if not team1 or not team2:
                            team_spans = row.find_all('span', class_=lambda x: x and ('TeamName' in x or 'abbr' in x or 'teamName' in x))
                            if len(team_spans) >= 2:
                                team1 = team_spans[0].text.strip()
                                team2 = team_spans[1].text.strip()
                        
                        # Third attempt - use the first two cells if they have content
                        if (not team1 or not team2) and len(team_cells) >= 2:
                            # Some tables have teams in first two cells
                            cell1_text = team_cells[0].text.strip()
                            cell2_text = team_cells[1].text.strip()
                            
                            # Ensure the cells contain team names (not just numbers/times)
                            if len(cell1_text) > 2 and not cell1_text[0].isdigit() and not ':' in cell1_text:
                                team1 = cell1_text
                            if len(cell2_text) > 2 and not cell2_text[0].isdigit() and not ':' in cell2_text:
                                team2 = cell2_text
                        
                        # If we still don't have team names, try one last approach for specific sports
                        if (not team1 or not team2) and sport in ['NBA', 'NHL']:
                            # These sports often have a single cell with "Team @ Team" format
                            for cell in team_cells:
                                cell_text = cell.text.strip()
                                if '@' in cell_text and len(cell_text.split('@')) == 2:
                                    teams = cell_text.split('@')
                                    team1 = teams[0].strip()
                                    team2 = teams[1].strip()
                                    break
                        
                        # If we still couldn't find teams, skip this row
                        if not team1 or not team2:
                            print(f"Skipping row in {sport} - could not identify teams")
                            print(f"--- SKIPPED PROCESSING: Could not identify teams ---\n")
                            continue
                        
                        # Clean up team names
                        team1 = team1.strip()
                        team2 = team2.strip()
                        
                        # Print detailed debug info for the Los Angeles teams
                        if 'los angeles' in team1.lower() or 'los angeles' in team2.lower():
                            print(f"DEBUG - Found LA team(s): '{team1}' vs '{team2}'")
                            print(f"  Team1 source: {type(team1)}, length: {len(team1)}")
                            print(f"  Team2 source: {type(team2)}, length: {len(team2)}")
                            
                            # Look for evidence of Angels vs Dodgers in the game ID or href
                            angels_dodgers_found = False
                            for cell in team_cells:
                                cell_html = str(cell)
                                if 'angels-dodgers' in cell_html:
                                    print(f"  Found Angels vs Dodgers in game ID!")
                                    team1 = "Los Angeles Angels"
                                    team2 = "Los Angeles Dodgers"
                                    angels_dodgers_found = True
                                    break
                            
                            # Print the raw HTML of the cells
                            for i, cell in enumerate(team_cells[:3]):
                                print(f"  Cell {i} HTML: {cell}")
                            
                            # If evidence found, don't continue with regular checks
                            if angels_dodgers_found:
                                print(f"Using identified teams: {team1} vs {team2}")

                        # Check if teams are duplicates (like "Los Angeles Angels vs Los Angeles Angels")
                        # Special case - if both are "Los Angeles" without specifics, check for more clues
                        if team1.lower() == team2.lower():
                            print(f"Skipping duplicate team matchup: {team1} vs {team2}")
                            print(f"--- SKIPPED PROCESSING: Duplicate team names ---\n")
                            continue
                        
                        # Get official team names from our dictionary
                        team1_official = get_official_team_name(sport, team1)
                        team2_official = get_official_team_name(sport, team2)
                        
                        # Extra debugging for Chicago teams
                        if 'chicago' in team1.lower() or 'chicago' in team2.lower():
                            print(f"DEBUG - Chicago team detection: '{team1}' vs '{team2}'")
                            print(f"  Official names: '{team1_official}' vs '{team2_official}'")
                            if team1_code:
                                print(f"  Team1 code: {team1_code}")
                            if team2_code:
                                print(f"  Team2 code: {team2_code}")
                        
                        # Extract team identifiers from URLs or classes to differentiate same-city teams
                        team1_code = None
                        team2_code = None
                        
                        # Look for team codes in href attributes
                        for cell in team_cells:
                            cell_html = str(cell)
                            # Try to extract team codes from href attributes
                            for link in cell.find_all('a', href=True):
                                href = link.get('href', '')
                                # Look for team codes in URL (typically after /name/)
                                if '/team/' in href and '/name/' in href:
                                    parts = href.split('/name/')
                                    if len(parts) > 1:
                                        code_parts = parts[1].split('/')
                                        if len(code_parts) > 0:
                                            code = code_parts[0].lower()
                                            
                                            # Check if this is the first or second team's link
                                            if link.text.strip().lower() == team1.lower() or team1.lower() in link.text.strip().lower():
                                                team1_code = code
                                                print(f"Found code for {team1}: {team1_code}")
                                            elif link.text.strip().lower() == team2.lower() or team2.lower() in link.text.strip().lower():
                                                team2_code = code
                                                print(f"Found code for {team2}: {team2_code}")
                        
                        # Use team codes (if found) to distinguish between same-city teams
                        if team1_official.lower() == team2_official.lower() and team1_code and team2_code and team1_code != team2_code:
                            print(f"Same city teams detected with different codes: {team1_code} vs {team2_code}")
                            
                            # Look for team code mappings in href or row
                            team_mapping = {}
                            for cell in team_cells:
                                cell_html = str(cell)
                                
                                # Check for known team codes in the entire row's HTML
                                if team1_code:
                                    if f"/{team1_code}/" in cell_html.lower() or f"{team1_code}." in cell_html.lower():
                                        for team in get_all_teams_for_sport(sport):
                                            if team1_code.lower() in team.lower() or team.lower() in team1_code:
                                                team_mapping[team1_code] = team
                                                break
                                
                                if team2_code:
                                    if f"/{team2_code}/" in cell_html.lower() or f"{team2_code}." in cell_html.lower():
                                        for team in get_all_teams_for_sport(sport):
                                            if team2_code.lower() in team.lower() or team.lower() in team2_code:
                                                team_mapping[team2_code] = team
                                                break
                            
                            # Update official names if we found mappings
                            if team1_code in team_mapping:
                                team1_official = team_mapping[team1_code]
                                print(f"Updated {team1} to {team1_official} using code {team1_code}")
                            
                            if team2_code in team_mapping:
                                team2_official = team_mapping[team2_code]
                                print(f"Updated {team2} to {team2_official} using code {team2_code}")
                        
                        # If team names are still the same, try to differentiate by looking at team codes
                        if team1_official.lower() == team2_official.lower() and team1_code and team2_code and team1_code != team2_code:
                            # Last resort - try to construct team names from city and codes
                            city_part = " ".join(team1_official.split()[:-1])  # Get the city part
                            
                            # Try to generate names based on codes - this is a fallback approach
                            sport_lowercase = sport.lower()
                            if sport_lowercase == 'mlb':
                                # MLB team code mappings
                                suffixes = {
                                    'chc': 'Cubs', 'chw': 'White Sox', 'cws': 'White Sox',
                                    'nyy': 'Yankees', 'nym': 'Mets',
                                    'laa': 'Angels', 'lad': 'Dodgers',
                                    'sf': 'Giants', 'oak': 'Athletics',
                                }
                                
                                if team1_code in suffixes:
                                    team1_official = f"{city_part} {suffixes[team1_code]}"
                                    print(f"Generated name for {team1}: {team1_official}")
                                
                                if team2_code in suffixes:
                                    team2_official = f"{city_part} {suffixes[team2_code]}"
                                    print(f"Generated name for {team2}: {team2_official}")
                                    
                            elif sport_lowercase == 'nhl':
                                # NHL codes like nyr/nyi for Rangers/Islanders
                                if city_part.lower() == 'new york':
                                    if team1_code == 'nyr':
                                        team1_official = 'New York Rangers'
                                    elif team1_code == 'nyi':
                                        team1_official = 'New York Islanders'
                                        
                                    if team2_code == 'nyr':
                                        team2_official = 'New York Rangers'
                                    elif team2_code == 'nyi':
                                        team2_official = 'New York Islanders'
                                
                                # LA Kings vs Anaheim Ducks
                                elif city_part.lower() == 'los angeles':
                                    if team1_code == 'lak':
                                        team1_official = 'Los Angeles Kings'
                                    elif team1_code == 'ana':
                                        team1_official = 'Anaheim Ducks'
                                        
                                    if team2_code == 'lak':
                                        team2_official = 'Los Angeles Kings'
                                    elif team2_code == 'ana':
                                        team2_official = 'Anaheim Ducks'
                        
                        # Check again after trying to differentiate
                        if team1_official.lower() == team2_official.lower():
                            print(f"Skipping duplicate team matchup (after differentiation): {team1_official} vs {team2_official}")
                            print(f"--- SKIPPED PROCESSING: Duplicate official team names ---\n")
                            continue
                        
                        # Create team keys based on full team name plus code if available
                        team1_key = team1_official.lower()
                        if team1_code:
                            team1_key += f"_{team1_code}"
                            
                        team2_key = team2_official.lower()
                        if team2_code:
                            team2_key += f"_{team2_code}"
                        
                        # Create a matchup key for detecting exact duplicate games
                        matchup_key = f"{team1_key}_{team2_key}"
                        matchup_key_reverse = f"{team2_key}_{team1_key}"
                        
                        # Check for game ID clues in case of same-city teams - using generic check
                        same_city_teams = False
                        if team1_code and team2_code and team1_code != team2_code:
                            print(f"Different team codes detected: {team1_code} vs {team2_code} - treating as different teams")
                            same_city_teams = True
                        
                        # Only skip if this exact matchup has already been processed
                        # Skip duplicate detection if we've identified this as a same-city matchup
                        if not same_city_teams and (matchup_key in processed_game_ids or matchup_key_reverse in processed_game_ids):
                            print(f"Skipping duplicate game: {team1_official} vs {team2_official} - already processed")
                            print(f"--- SKIPPED PROCESSING: Duplicate matchup already processed ---\n")
                            continue
                        
                        # Initialize result data
                        game_result = None
                        winner = None
                        loser = None
                        
                        # Look for game results for completed games (by checking RESULT column)
                        result_cells = row.find_all('td', class_='Table__TD', attrs={'data-header': 'RESULT'})
                        if not result_cells:
                            # Try direct column name matching as well
                            result_cells = row.find_all('td', string=lambda x: x and 'RESULT' in x)
                            
                        if result_cells:
                            result_cell = result_cells[0]
                            result_text = result_cell.text.strip()
                            print(f"Found result cell with text: '{result_text}'")
                            
                            # Check for common result formats (e.g., "NYM 3, NYY 2")
                            game_status = "completed"
                            game_result = result_text
                            
                            # Try to find winner/loser cells
                            win_cells = row.find_all('td', class_='Table__TD', attrs={'data-header': 'WIN'})
                            loss_cells = row.find_all('td', class_='Table__TD', attrs={'data-header': 'LOSS'})
                            
                            if win_cells:
                                winner = win_cells[0].text.strip()
                                print(f"Found winner: {winner}")
                            
                            if loss_cells:
                                loser = loss_cells[0].text.strip()
                                print(f"Found loser: {loser}")
                        
                        # Get game time - look for time in different possible cells
                        time_cell = None
                        time_text = None
                        
                        print(f"\n--- PROCESSING GAME: {team1} vs {team2} ---")
                        
                        # Look for game time in different cells - varies by sport
                        for cell in team_cells:
                            cell_text = cell.text.strip()
                            cell_class = cell.get('class', [])
                            
                            # Check for date_col class which often contains time
                            if 'date__col' in cell_class or ':' in cell_text or 'LIVE' in cell_text or 'PM' in cell_text or 'AM' in cell_text:
                                time_cell = cell
                                time_text = cell_text
                                print(f"Found time cell with text: '{time_text}' (class: {cell_class})")
                                break
                        
                        # If no time cell was found, look for gameStatus cells specifically
                        if not time_text:
                            game_status_cells = row.find_all('td', class_=lambda x: x and ('gameStatus' in x.lower() or 'game-status' in x.lower()))
                            if game_status_cells:
                                time_text = game_status_cells[0].text.strip()
                        
                        # If still no time, check if there's a cell with just time pattern
                        if not time_text:
                            for cell in team_cells:
                                cell_text = cell.text.strip()
                                # Look for typical time formats (e.g., 8:00 PM)
                                if re.search(r'\d{1,2}:\d{2}\s*(?:AM|PM|ET|EST|EDT)?', cell_text):
                                    time_text = cell_text
                                    break
                                # Also check for any in-progress or live status indicators
                                elif any(status in cell_text.upper() for status in ['LIVE', 'IN PROGRESS', 'ONGOING']):
                                    time_text = 'LIVE'
                                    break
                        
                        # If we still don't have a time, check for game status in the entire row
                        if not time_text:
                            row_text = row.text.strip().upper()
                            print(f"Checking row text for live indicators: '{row_text}'")
                            if any(status in row_text for status in ['LIVE', 'IN PROGRESS', 'ONGOING']):
                                time_text = 'LIVE'
                                print(f"Found LIVE status in row text")
                            else:
                                print(f"Skipping {team1} vs {team2} - no time found")
                                print(f"--- SKIPPED PROCESSING: No time information ---\n")
                                continue
                        
                        # Skip games with TBD, Postponed or PPD
                        if any(status in time_text for status in ['TBD', 'Postponed', 'PPD']):
                            print(f"Skipping {team1} vs {team2} - time is {time_text}")
                            print(f"--- SKIPPED PROCESSING: Game status is {time_text} ---\n")
                            continue
                        
                        # Check if game is final, in progress, or scheduled
                        game_status = "upcoming"
                        if "LIVE" in time_text.upper() or "IN PROGRESS" in time_text.upper():
                            game_status = "live"
                            print(f"Setting game status to LIVE: {team1} vs {team2}")
                            
                            # Also ensure any content with the word "LIVE" is captured
                            for cell in team_cells:
                                cell_content = cell.text.strip().upper()
                                if "LIVE" in cell_content:
                                    print(f"Found additional LIVE indicator in cell text: {cell_content}")
                        elif "FINAL" in time_text.upper() or "F/" in time_text.upper():
                            # Process games that are already finished
                            game_status = "completed"
                            print(f"Setting game status to COMPLETED: {team1} vs {team2}")
                            
                            # Extract result if available
                            result_text = "Final"
                            # Look for a score in the time text (common format: "F 5-3")
                            score_match = re.search(r'F\s+(\d+)[^\d]+(\d+)', time_text)
                            if score_match:
                                result_text = f"{score_match.group(1)}-{score_match.group(2)}"
                                print(f"Extracted score from time: {result_text}")
                            
                            # If we don't have a score yet, check all cells for score patterns
                            if result_text == "Final":
                                for cell in team_cells:
                                    cell_text = cell.text.strip()
                                    # Look for common score patterns like "5-3", "W 5-3", etc.
                                    score_match = re.search(r'(?:^|\s)(\d+)[-\s]+(\d+)(?:\s|$)', cell_text)
                                    if score_match:
                                        result_text = f"{score_match.group(1)}-{score_match.group(2)}"
                                        print(f"Found score in cell: {result_text} from '{cell_text}'")
                                        break
                            
                            # If we already have a game_result from result column, use that instead
                            if game_result:
                                result_text = game_result
                                print(f"Using result from column: {result_text}")
                            else:
                                game_result = result_text
                            
                            # Look for WIN/LOSS information if we don't have it already
                            if not winner or not loser:
                                # Try to find specific win/loss cells or pitcher information
                                for cell in team_cells:
                                    cell_text = cell.text.strip()
                                    # Look for WIN: Player patterns
                                    win_match = re.search(r'(?:WIN|W):\s*([^,;]+)', cell_text, re.IGNORECASE)
                                    if win_match and not winner:
                                        winner = win_match.group(1).strip()
                                        print(f"Extracted winner: {winner}")
                                    
                                    # Look for LOSS: Player patterns
                                    loss_match = re.search(r'(?:LOSS|L):\s*([^,;]+)', cell_text, re.IGNORECASE)
                                    if loss_match and not loser:
                                        loser = loss_match.group(1).strip()
                                        print(f"Extracted loser: {loser}")
                        
                        # Also check status columns for FINAL indicators if game is not already marked as completed
                        if game_status != "completed" and game_status != "live":
                            for cell in team_cells:
                                cell_content = cell.text.strip().upper()
                                # Look for FINAL, F, F/OT (Final in Overtime)
                                if re.search(r'\b(FINAL|F(/\w+)?)\b', cell_content):
                                    print(f"Found FINAL indicator in cell: {cell_content}")
                                    game_status = "completed"
                                    game_result = "Final"
                                    
                                    # Try to extract score from this cell or surrounding cells
                                    score_match = re.search(r'(\d+)[-\s]+(\d+)', cell_content)
                                    if score_match:
                                        game_result = f"{score_match.group(1)}-{score_match.group(2)}"
                                        print(f"Extracted score from final cell: {game_result}")
                                    break
                            
                        if game_status == "live":
                            # Game is live, set time to now
                            game_time = datetime.now()
                            
                            # Create a unique ID for this LIVE game
                            unique_game_id = f"{game_id}_{team1_official.lower().replace(' ', '')}_{team2_official.lower().replace(' ', '')}_{game_time.strftime('%H%M')}_LIVE"
                            
                            # Add this matchup to processed games to prevent actual duplicates
                            matchup_key = f"{team1_key}_{team2_key}"
                            processed_game_ids.add(matchup_key)
                            
                            # Mark both teams as having a game today
                            teams_with_games_today.add(team1_key)
                            teams_with_games_today.add(team2_key)
                            
                            # Print successfully parsed time for LIVE game
                            print(f"Successfully parsed LIVE game: {team1_official} vs {team2_official} at {game_time.strftime('%I:%M %p %Z on %Y-%m-%d')} [ID: {unique_game_id}]")
                            print(f"--- DONE PROCESSING GAME: {team1_official} vs {team2_official} ---\n")
                            
                            # Create various matchup formats for better matching
                            # Standard format with official team names - keep order consistent
                            sorted_teams = sorted([team1_official, team2_official])
                            std_matchup = f"{sorted_teams[0]} vs {sorted_teams[1]}"
                            
                            # Create an exact matchup key with team order preserved
                            exact_matchup = f"{team1_official} vs {team2_official}"
                            exact_matchup_reverse = f"{team2_official} vs {team1_official}"
                            
                            # Create a consistent matchup key for easier comparison
                            matchup_key = f"{sorted_teams[0].lower()} vs {sorted_teams[1].lower()}"
                            
                            # Convert the time to ET timezone for consistency
                            et_tz = pytz.timezone('US/Eastern')
                            game_time = et_tz.localize(game_time)
                            
                            # Store game info including status, start time, league, and both teams
                            time_info = {
                                'utc_time': game_time.astimezone(pytz.UTC).isoformat(),
                                'local_time': game_time.strftime('%I:%M %p %Z'),
                                'start_time': 'LIVE',
                                'status': game_status,
                                'league': sport,
                                'matchup': exact_matchup,
                                'matchup_key': matchup_key,
                                'game_id': unique_game_id,
                                'row_position': row_position,
                                'table_position': table_idx,
                                'game_date': game_time.date().strftime('%Y-%m-%d'),
                                'section_date': section_date.strftime('%Y-%m-%d'),
                                'teams': {
                                    'team1': team1_official,
                                    'team2': team2_official,
                                    'team1_original': team1,
                                    'team2_original': team2
                                }
                            }
                            
                            # Store both exact matchups with the game ID - this is crucial for accurate lookup
                            # Add "LIVE" to key for live games to prevent overwriting with stale info
                            key_suffix = "_LIVE"  # Always _LIVE for live games
                            game_times[f"{exact_matchup}_{unique_game_id}{key_suffix}"] = time_info
                            game_times[f"{exact_matchup_reverse}_{unique_game_id}{key_suffix}"] = time_info
                            
                            # Store individual team information for team-based lookups
                            if 'team_games' not in game_times:
                                game_times['team_games'] = {}
                                
                            # Index by normalized team names for both teams
                            for team_idx, team in enumerate([team1_official, team2_official]):
                                # Store team names in lowercase for easier matching later
                                normalized = team.lower()
                                # Remove common suffixes and special characters
                                normalized = re.sub(r'\s+(FC|Team)$', '', normalized)
                                normalized = re.sub(r'[^\w\s]', '', normalized).strip()
                                
                                # Create or append to the team's game list
                                if normalized not in game_times['team_games']:
                                    game_times['team_games'][normalized] = []
                                
                                # Only add if not already in the list
                                if not any(g['game_id'] == unique_game_id for g in game_times['team_games'][normalized]):
                                    # Store which position this team is in the matchup (team1 or team2)
                                    team_position = 'team1' if team_idx == 0 else 'team2'
                                    
                                    # Create a copy of time_info with the team's position
                                    team_info = dict(time_info)
                                    team_info['is_team1'] = team_position == 'team1'
                                    team_info['team_normalized'] = normalized
                                    team_info['other_team'] = team2_official.lower() if team_idx == 0 else team1_official.lower()
                                    
                                    game_times['team_games'][normalized].append(team_info)
                                    
                                # Also store single-word variations for teams with multiple words
                                words = normalized.split()
                                if len(words) > 1:
                                    for word in words:
                                        if len(word) > 3:  # Only use words longer than 3 chars
                                            if word not in game_times['team_games']:
                                                game_times['team_games'][word] = []
                                            
                                            # Only add if not already in the list with same info
                                            if not any(g['game_id'] == unique_game_id for g in game_times['team_games'][word]):
                                                # Store which position this team is in the matchup
                                                team_position = 'team1' if team_idx == 0 else 'team2'
                                                
                                                # Create a copy of time_info with the team's position
                                                team_info = dict(time_info)
                                                team_info['is_team1'] = team_position == 'team1'
                                                team_info['team_normalized'] = normalized
                                                team_info['word_match'] = True
                                                team_info['other_team'] = team2_official.lower() if team_idx == 0 else team1_official.lower()
                                                
                                                game_times['team_games'][word].append(team_info)
                                
                        elif game_status == "completed":
                            # Game is completed, no countdown needed
                            # Create a unique ID for this completed game
                            unique_game_id = f"{game_id}_{team1_official.lower().replace(' ', '')}_{team2_official.lower().replace(' ', '')}_{datetime.now().strftime('%H%M')}_COMPLETED"
                            
                            # Add this matchup to processed games to prevent actual duplicates
                            matchup_key = f"{team1_key}_{team2_key}"
                            processed_game_ids.add(matchup_key)
                            
                            # Mark both teams as having a game today
                            teams_with_games_today.add(team1_key)
                            teams_with_games_today.add(team2_key)
                            
                            # Print successfully parsed completed game
                            print(f"Successfully parsed COMPLETED game: {team1_official} vs {team2_official} with result: {game_result} [ID: {unique_game_id}]")
                            print(f"--- DONE PROCESSING GAME: {team1_official} vs {team2_official} ---\n")
                            
                            # Create various matchup formats for better matching
                            # Standard format with official team names - keep order consistent
                            sorted_teams = sorted([team1_official, team2_official])
                            std_matchup = f"{sorted_teams[0]} vs {sorted_teams[1]}"
                            
                            # Create an exact matchup key with team order preserved
                            exact_matchup = f"{team1_official} vs {team2_official}"
                            exact_matchup_reverse = f"{team2_official} vs {team1_official}"
                            
                            # Create a consistent matchup key for easier comparison
                            matchup_key = f"{sorted_teams[0].lower()} vs {sorted_teams[1].lower()}"
                            
                            # Use current time for completed games
                            game_time = datetime.now()
                            
                            # Convert the time to ET timezone for consistency
                            et_tz = pytz.timezone('US/Eastern')
                            game_time = et_tz.localize(game_time)
                            
                            # Store game info including status, result, league, and both teams
                            time_info = {
                                'utc_time': game_time.astimezone(pytz.UTC).isoformat(),
                                'local_time': game_time.strftime('%I:%M %p %Z'),
                                'start_time': 'COMPLETED',
                                'status': game_status,
                                'league': sport,
                                'matchup': exact_matchup,
                                'matchup_key': matchup_key,
                                'game_id': unique_game_id,
                                'row_position': row_position,
                                'table_position': table_idx,
                                'game_date': game_time.date().strftime('%Y-%m-%d'),
                                'section_date': section_date.strftime('%Y-%m-%d'),
                                'result': game_result,
                                'winner': winner,
                                'loser': loser,
                                'teams': {
                                    'team1': team1_official,
                                    'team2': team2_official,
                                    'team1_original': team1,
                                    'team2_original': team2
                                }
                            }
                            
                            # Store both exact matchups with the game ID - this is crucial for accurate lookup
                            # Add "COMPLETED" to key for completed games
                            key_suffix = "_COMPLETED"
                            game_times[f"{exact_matchup}_{unique_game_id}{key_suffix}"] = time_info
                            game_times[f"{exact_matchup_reverse}_{unique_game_id}{key_suffix}"] = time_info
                            
                            # Store individual team information for team-based lookups
                            if 'team_games' not in game_times:
                                game_times['team_games'] = {}
                                
                            # Index by normalized team names for both teams
                            for team_idx, team in enumerate([team1_official, team2_official]):
                                # Store team names in lowercase for easier matching later
                                normalized = team.lower()
                                # Remove common suffixes and special characters
                                normalized = re.sub(r'\s+(FC|Team)$', '', normalized)
                                normalized = re.sub(r'[^\w\s]', '', normalized).strip()
                                
                                # Create or append to the team's game list
                                if normalized not in game_times['team_games']:
                                    game_times['team_games'][normalized] = []
                                
                                # Only add if not already in the list
                                if not any(g['game_id'] == unique_game_id for g in game_times['team_games'][normalized]):
                                    # Store which position this team is in the matchup (team1 or team2)
                                    team_position = 'team1' if team_idx == 0 else 'team2'
                                    
                                    # Create a copy of time_info with the team's position
                                    team_info = dict(time_info)
                                    team_info['is_team1'] = team_position == 'team1'
                                    team_info['team_normalized'] = normalized
                                    team_info['other_team'] = team2_official.lower() if team_idx == 0 else team1_official.lower()
                                    
                                    game_times['team_games'][normalized].append(team_info)
                                    
                                # Also store single-word variations for teams with multiple words
                                words = normalized.split()
                                if len(words) > 1:
                                    for word in words:
                                        if len(word) > 3:  # Only use words longer than 3 chars
                                            if word not in game_times['team_games']:
                                                game_times['team_games'][word] = []
                                            
                                            # Only add if not already in the list with same info
                                            if not any(g['game_id'] == unique_game_id for g in game_times['team_games'][word]):
                                                # Store which position this team is in the matchup
                                                team_position = 'team1' if team_idx == 0 else 'team2'
                                                
                                                # Create a copy of time_info with the team's position
                                                team_info = dict(time_info)
                                                team_info['is_team1'] = team_position == 'team1'
                                                team_info['team_normalized'] = normalized
                                                team_info['word_match'] = True
                                                team_info['other_team'] = team2_official.lower() if team_idx == 0 else team1_official.lower()
                                                
                                                game_times['team_games'][word].append(team_info)
                        
                        elif time_text and ":" in time_text and ("ET" in time_text or "PM" in time_text or "AM" in time_text):
                            # Regular time format
                            # Extract just the time part
                            time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM)?)', time_text)
                            if time_match:
                                time_parts = time_match.group(1).strip()
                            else:
                                time_parts = time_text.replace('ET', '').strip()
                            
                            try:
                                # Try different time formats
                                try:
                                    # If AM/PM is specified
                                    game_time = datetime.strptime(time_parts, '%I:%M %p')
                                except ValueError:
                                    try:
                                        # If only hours and minutes
                                        if ':' in time_parts:
                                            if 'PM' in time_text and not 'PM' in time_parts:
                                                # Add PM if it's in the original text but not the extracted part
                                                hours, minutes = map(int, time_parts.split(':'))
                                                if hours < 12:  # Convert to 24 hour format if PM
                                                    hours += 12
                                                game_time = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
                                            elif 'AM' in time_text and not 'AM' in time_parts:
                                                # Keep AM time as is
                                                hours, minutes = map(int, time_parts.split(':'))
                                                game_time = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
                                            else:
                                                # Default to standard 24-hour format
                                                game_time = datetime.strptime(time_parts, '%H:%M')
                                        else:
                                            raise ValueError("Invalid time format")
                                    except ValueError:
                                        print(f"Could not parse time: {time_text} for {team1} vs {team2}")
                                        print(f"--- SKIPPED PROCESSING: Time parsing error ---\n")
                                        continue
                                
                                # IMPORTANT: Use the section date for this game
                                game_time = game_time.replace(
                                    year=section_date.year,
                                    month=section_date.month,
                                    day=section_date.day
                                )
                                
                                # Convert to user's local time (assume Eastern Time)
                                et_tz = pytz.timezone('US/Eastern')
                                game_time = et_tz.localize(game_time)
                                
                                # Create a unique ID for this game based on teams and time
                                unique_game_id = f"{game_id}_{team1_official.lower().replace(' ', '')}_{team2_official.lower().replace(' ', '')}_{game_time.strftime('%H%M')}"
                                
                                # Skip adding the matchup key check here - we already did it earlier
                                # This avoids redundant checks and allows teams from the same city to play each other
                                
                                # Add this matchup to processed games to prevent actual duplicates
                                matchup_key = f"{team1_key}_{team2_key}"
                                processed_game_ids.add(matchup_key)
                                
                                # Now that we're going to use this game, mark both teams as having a game today
                                teams_with_games_today.add(team1_key)
                                teams_with_games_today.add(team2_key)
                                
                                # Print successfully parsed time
                                print(f"Successfully parsed game: {team1_official} vs {team2_official} at {game_time.strftime('%I:%M %p %Z on %Y-%m-%d')} [ID: {unique_game_id}]")
                                print(f"--- DONE PROCESSING GAME: {team1_official} vs {team2_official} ---\n")
                                
                                # Create various matchup formats for better matching
                                # Standard format with official team names - keep order consistent
                                sorted_teams = sorted([team1_official, team2_official])
                                std_matchup = f"{sorted_teams[0]} vs {sorted_teams[1]}"
                                
                                # Create an exact matchup key with team order preserved
                                exact_matchup = f"{team1_official} vs {team2_official}"
                                exact_matchup_reverse = f"{team2_official} vs {team1_official}"
                                
                                # Create a consistent matchup key for easier comparison
                                matchup_key = f"{sorted_teams[0].lower()} vs {sorted_teams[1].lower()}"
                                
                                # Store game info including status, start time, league, and both teams
                                time_info = {
                                    'utc_time': game_time.astimezone(pytz.UTC).isoformat(),
                                    'local_time': game_time.strftime('%I:%M %p %Z'),
                                    'start_time': game_time.strftime('%I:%M %p'),
                                    'status': game_status,
                                    'league': sport,
                                    'matchup': exact_matchup,
                                    'matchup_key': matchup_key,
                                    'game_id': unique_game_id,
                                    'row_position': row_position,
                                    'table_position': table_idx,
                                    'game_date': game_time.date().strftime('%Y-%m-%d'),
                                    'section_date': section_date.strftime('%Y-%m-%d'),
                                    'teams': {
                                        'team1': team1_official,
                                        'team2': team2_official,
                                        'team1_original': team1,
                                        'team2_original': team2
                                    }
                                }
                                
                                # Store both exact matchups with the game ID - this is crucial for accurate lookup
                                # Add "LIVE" to key for live games to prevent overwriting with stale info
                                key_suffix = "_LIVE" if game_status == "live" else ""
                                game_times[f"{exact_matchup}_{unique_game_id}{key_suffix}"] = time_info
                                game_times[f"{exact_matchup_reverse}_{unique_game_id}{key_suffix}"] = time_info
                                
                                # Store individual team information for team-based lookups
                                # This allows us to match games by any team mentioned in the matchup
                                if 'team_games' not in game_times:
                                    game_times['team_games'] = {}
                                    
                                # Index by normalized team names - both exact form and with standardized team order
                                for team_idx, team in enumerate([team1_official, team2_official]):
                                    # Store team names in lowercase for easier matching later
                                    normalized = team.lower()
                                    # Remove common suffixes and special characters
                                    normalized = re.sub(r'\s+(FC|Team)$', '', normalized)
                                    normalized = re.sub(r'[^\w\s]', '', normalized).strip()
                                    
                                    # Create or append to the team's game list
                                    if normalized not in game_times['team_games']:
                                        game_times['team_games'][normalized] = []
                                    
                                    # Only add if not already in the list
                                    if not any(g['game_id'] == unique_game_id for g in game_times['team_games'][normalized]):
                                        # Store which position this team is in the matchup (team1 or team2)
                                        # This is crucial for correctly matching teams across sources
                                        team_position = 'team1' if team_idx == 0 else 'team2'
                                        
                                        # Create a copy of time_info with the team's position
                                        team_info = dict(time_info)
                                        team_info['is_team1'] = team_position == 'team1'
                                        team_info['team_normalized'] = normalized
                                        team_info['other_team'] = team2_official.lower() if team_idx == 0 else team1_official.lower()
                                        
                                        game_times['team_games'][normalized].append(team_info)
                                        
                                    # Also store single-word variations for teams with multiple words
                                    words = normalized.split()
                                    if len(words) > 1:
                                        for word in words:
                                            if len(word) > 3:  # Only use words longer than 3 chars
                                                if word not in game_times['team_games']:
                                                    game_times['team_games'][word] = []
                                                
                                                # Only add if not already in the list with same info
                                                if not any(g['game_id'] == unique_game_id for g in game_times['team_games'][word]):
                                                    # Store which position this team is in the matchup
                                                    team_position = 'team1' if team_idx == 0 else 'team2'
                                                    
                                                    # Create a copy of time_info with the team's position
                                                    team_info = dict(time_info)
                                                    team_info['is_team1'] = team_position == 'team1'
                                                    team_info['team_normalized'] = normalized
                                                    team_info['word_match'] = True
                                                    team_info['other_team'] = team2_official.lower() if team_idx == 0 else team1_official.lower()
                                                    
                                                    game_times['team_games'][word].append(team_info)
                                
                            except ValueError as e:
                                print(f"Time parsing error: {e} for {time_text}")
                                print(f"--- SKIPPED PROCESSING: Time parsing error ---\n")
                                continue
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

def get_official_team_name(sport, team_name):
    """Get the official team name from our dictionary of teams with improved matching."""
    if not team_name:
        return team_name
        
    # Dictionary of sports and their teams
    sports_teams = {
        'NBA': {
            'Boston Celtics', 'Brooklyn Nets', 'New York Knicks', 'Philadelphia 76ers', 'Toronto Raptors',
            'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers', 'Milwaukee Bucks',
            'Atlanta Hawks', 'Charlotte Hornets', 'Miami Heat', 'Orlando Magic', 'Washington Wizards',
            'Denver Nuggets', 'Minnesota Timberwolves', 'Oklahoma City Thunder', 'Portland Trail Blazers', 'Utah Jazz',
            'Golden State Warriors', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Phoenix Suns', 'Sacramento Kings',
            'Dallas Mavericks', 'Houston Rockets', 'Memphis Grizzlies', 'New Orleans Pelicans', 'San Antonio Spurs'
        },
        'NFL': {
            'Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills', 'Carolina Panthers',
            'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns', 'Dallas Cowboys', 'Denver Broncos',
            'Detroit Lions', 'Green Bay Packers', 'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars',
            'Kansas City Chiefs', 'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
            'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants', 'New York Jets',
            'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers', 'Seattle Seahawks', 'Tampa Bay Buccaneers',
            'Tennessee Titans', 'Washington Commanders'
        },
        'MLB': {
            'Arizona Diamondbacks', 'Atlanta Braves', 'Baltimore Orioles', 'Boston Red Sox', 'Chicago Cubs',
            'Chicago White Sox', 'Cincinnati Reds', 'Cleveland Guardians', 'Colorado Rockies', 'Detroit Tigers',
            'Houston Astros', 'Kansas City Royals', 'Los Angeles Angels', 'Los Angeles Dodgers', 'Miami Marlins',
            'Milwaukee Brewers', 'Minnesota Twins', 'New York Mets', 'New York Yankees', 'Oakland Athletics',
            'Philadelphia Phillies', 'Pittsburgh Pirates', 'San Diego Padres', 'San Francisco Giants', 'Seattle Mariners',
            'St. Louis Cardinals', 'Tampa Bay Rays', 'Texas Rangers', 'Toronto Blue Jays', 'Washington Nationals'
        },
        'NHL': {
            'Anaheim Ducks', 'Arizona Coyotes', 'Boston Bruins', 'Buffalo Sabres', 'Calgary Flames',
            'Carolina Hurricanes', 'Chicago Blackhawks', 'Colorado Avalanche', 'Columbus Blue Jackets', 'Dallas Stars',
            'Detroit Red Wings', 'Edmonton Oilers', 'Florida Panthers', 'Los Angeles Kings', 'Minnesota Wild',
            'Montreal Canadiens', 'Nashville Predators', 'New Jersey Devils', 'New York Islanders', 'New York Rangers',
            'Ottawa Senators', 'Philadelphia Flyers', 'Pittsburgh Penguins', 'San Jose Sharks', 'Seattle Kraken',
            'St. Louis Blues', 'Tampa Bay Lightning', 'Toronto Maple Leafs', 'Vancouver Canucks', 'Vegas Golden Knights',
            'Washington Capitals', 'Winnipeg Jets'
        }
    }
    
    # Special abbreviations for ESPN teams
    espn_abbreviations = {
        'NBA': {
            'GS': 'Golden State Warriors',
            'SA': 'San Antonio Spurs',
            'NO': 'New Orleans Pelicans',
            'NY': 'New York Knicks',
            'OKC': 'Oklahoma City Thunder',
            'LAL': 'Los Angeles Lakers',
            'LAC': 'Los Angeles Clippers',
            'CHA': 'Charlotte Hornets',
            'CLE': 'Cleveland Cavaliers',
            'WAS': 'Washington Wizards',
            'PHI': 'Philadelphia 76ers',
            'PHX': 'Phoenix Suns',
            'POR': 'Portland Trail Blazers'
        },
        'NFL': {
            'SF': 'San Francisco 49ers',
            'NO': 'New Orleans Saints',
            'TB': 'Tampa Bay Buccaneers',
            'GB': 'Green Bay Packers',
            'KC': 'Kansas City Chiefs',
            'NE': 'New England Patriots',
            'LV': 'Las Vegas Raiders',
            'NYG': 'New York Giants',
            'NYJ': 'New York Jets',
            'WSH': 'Washington Commanders',
            'JAX': 'Jacksonville Jaguars',
            'LAR': 'Los Angeles Rams',
            'LAC': 'Los Angeles Chargers'
        },
        'MLB': {
            'SF': 'San Francisco Giants',
            'SD': 'San Diego Padres',
            'CWS': 'Chicago White Sox',
            'CHC': 'Chicago Cubs',
            'NYY': 'New York Yankees',
            'NYM': 'New York Mets',
            'STL': 'St. Louis Cardinals',
            'KC': 'Kansas City Royals',
            'TB': 'Tampa Bay Rays',
            'LAD': 'Los Angeles Dodgers',
            'LA': 'Los Angeles Angels',
            'LAA': 'Los Angeles Angels',
            'CHW': 'Chicago White Sox'
        },
        'NHL': {
            'SJ': 'San Jose Sharks',
            'TB': 'Tampa Bay Lightning',
            'NJ': 'New Jersey Devils',
            'VGK': 'Vegas Golden Knights',
            'LA': 'Los Angeles Kings',
            'CBJ': 'Columbus Blue Jackets',
            'NYR': 'New York Rangers',
            'NYI': 'New York Islanders',
            'TOR': 'Toronto Maple Leafs',
            'MTL': 'Montreal Canadiens',
            'VAN': 'Vancouver Canucks',
            'WSH': 'Washington Capitals',
            'EDM': 'Edmonton Oilers',
            'CGY': 'Calgary Flames',
            'TBL': 'Tampa Bay Lightning',
            'NSH': 'Nashville Predators',
            'STL': 'St. Louis Blues',
            'CHI': 'Chicago Blackhawks'
        }
    }
    
    # Clean input
    team_name_clean = team_name.strip()
    team_name_lower = team_name_clean.lower()
    
    # Try to find the best match
    if sport in sports_teams:
        # First check for same-city teams using identifiable keywords
        
        # Special handling for New York teams (Yankees/Mets)
        if sport == 'MLB' and team_name_lower in ['new york', 'ny']:
            print(f"Handling New York MLB team: '{team_name}'")
            # Try to use more context to determine which NY team
            if 'yankee' in team_name_lower or 'nyy' in team_name_lower or 'yanks' in team_name_lower:
                return 'New York Yankees'
            elif 'met' in team_name_lower or 'nym' in team_name_lower or 'mets' in team_name_lower:
                return 'New York Mets'
            # Default to Mets for now if no clear indicators (can adjust based on frequency)
            # Note: This is a best guess when we just have "New York"
            return 'New York Yankees'
            
        # Special handling for Los Angeles teams (Angels/Dodgers)
        if sport == 'MLB' and team_name_lower in ['los angeles', 'la']:
            print(f"Handling Los Angeles MLB team: '{team_name}'")
            # Try to use context clues
            if 'angel' in team_name_lower or 'ana' in team_name_lower or 'laa' in team_name_lower:
                return 'Los Angeles Angels'
            elif 'dodger' in team_name_lower or 'lad' in team_name_lower or 'dodgers' in team_name_lower:
                return 'Los Angeles Dodgers'
            # Default to Dodgers if unclear
            return 'Los Angeles Dodgers'
            
        # Special handling for Chicago teams (Cubs/White Sox)
        if sport == 'MLB' and team_name_lower in ['chicago', 'chi']:
            print(f"Handling Chicago MLB team: '{team_name}'")
            # Try to determine which Chicago team
            if 'cub' in team_name_lower or 'chc' in team_name_lower:
                return 'Chicago Cubs'
            elif 'white' in team_name_lower or 'sox' in team_name_lower or 'chw' in team_name_lower or 'cws' in team_name_lower:
                return 'Chicago White Sox'
            
            # Instead of defaulting, handle this in the team differentiation code
            # and keep the name as "Chicago" to allow proper differentiation
            return team_name
        
        # 1. Check for abbreviation first (exact match only)
        if sport in espn_abbreviations and team_name_clean in espn_abbreviations[sport]:
            return espn_abbreviations[sport][team_name_clean]
        
        # 2. Try exact match
        for official_name in sports_teams[sport]:
            if official_name.lower() == team_name_lower:
                return official_name
                
        # Handle Los Angeles teams with more context
        if sport == 'MLB' and 'los angeles' in team_name_lower:
            if 'angel' in team_name_lower or 'ana' in team_name_lower or 'laa' in team_name_lower:
                return 'Los Angeles Angels'
            elif 'dodger' in team_name_lower or 'lad' in team_name_lower:
                return 'Los Angeles Dodgers'
                
        # Handle New York teams with more context
        if sport == 'MLB' and 'new york' in team_name_lower:
            if 'yankee' in team_name_lower or 'nyy' in team_name_lower or 'yanks' in team_name_lower:
                return 'New York Yankees'
            elif 'met' in team_name_lower or 'nym' in team_name_lower or 'mets' in team_name_lower:
                return 'New York Mets'
                
        # Handle Chicago teams with more context
        if sport == 'MLB' and 'chicago' in team_name_lower:
            if 'cub' in team_name_lower or 'chc' in team_name_lower:
                return 'Chicago Cubs'
            elif 'white' in team_name_lower or 'sox' in team_name_lower or 'chw' in team_name_lower:
                return 'Chicago White Sox'
        
        # 3. Try partial match with city, prioritizing suffix match 
        for official_name in sports_teams[sport]:
            official_parts = official_name.split()
            if len(official_parts) < 2:
                continue
                
            # Get city and nickname separately
            official_city = official_parts[0].lower()
            official_nickname = ' '.join(official_parts[1:]).lower()
            
            # Check if team name is just the city or just the nickname
            if official_city == team_name_lower or official_nickname == team_name_lower:
                return official_name
                
            # Check if the team name contains both city and part of nickname or vice versa
            if (official_city in team_name_lower and any(part in team_name_lower for part in official_nickname.split())) or \
               (official_nickname in team_name_lower and official_city in team_name_lower):
                return official_name
                
        # 4. Try more lenient matching, but requiring the match to be distinctive
        best_match = None
        highest_score = 0
        
        for official_name in sports_teams[sport]:
            # Skip if there's no substantial overlap at all
            if not any(word in team_name_lower for word in official_name.lower().split()):
                continue
                
            # Calculate match score based on word overlap
            official_words = set(official_name.lower().split())
            input_words = set(team_name_lower.split())
            
            common_words = official_words.intersection(input_words)
            if not common_words:
                continue
                
            # Score is the proportion of matching words
            match_score = len(common_words) / max(len(official_words), len(input_words))
            
            if match_score > highest_score:
                highest_score = match_score
                best_match = official_name
                
        if best_match and highest_score > 0.3:  # Threshold to avoid false matches
            return best_match
                
    # If no match found, return the original
    return team_name

def get_all_teams_for_sport(sport):
    """Return a list of all official team names for a given sport."""
    # Dictionary of sports and their teams
    sports_teams = {
        'NBA': {
            'Boston Celtics', 'Brooklyn Nets', 'New York Knicks', 'Philadelphia 76ers', 'Toronto Raptors',
            'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers', 'Milwaukee Bucks',
            'Atlanta Hawks', 'Charlotte Hornets', 'Miami Heat', 'Orlando Magic', 'Washington Wizards',
            'Denver Nuggets', 'Minnesota Timberwolves', 'Oklahoma City Thunder', 'Portland Trail Blazers', 'Utah Jazz',
            'Golden State Warriors', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Phoenix Suns', 'Sacramento Kings',
            'Dallas Mavericks', 'Houston Rockets', 'Memphis Grizzlies', 'New Orleans Pelicans', 'San Antonio Spurs'
        },
        'NFL': {
            'Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills', 'Carolina Panthers',
            'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns', 'Dallas Cowboys', 'Denver Broncos',
            'Detroit Lions', 'Green Bay Packers', 'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars',
            'Kansas City Chiefs', 'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
            'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants', 'New York Jets',
            'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers', 'Seattle Seahawks', 'Tampa Bay Buccaneers',
            'Tennessee Titans', 'Washington Commanders'
        },
        'MLB': {
            'Arizona Diamondbacks', 'Atlanta Braves', 'Baltimore Orioles', 'Boston Red Sox', 'Chicago Cubs',
            'Chicago White Sox', 'Cincinnati Reds', 'Cleveland Guardians', 'Colorado Rockies', 'Detroit Tigers',
            'Houston Astros', 'Kansas City Royals', 'Los Angeles Angels', 'Los Angeles Dodgers', 'Miami Marlins',
            'Milwaukee Brewers', 'Minnesota Twins', 'New York Mets', 'New York Yankees', 'Oakland Athletics',
            'Philadelphia Phillies', 'Pittsburgh Pirates', 'San Diego Padres', 'San Francisco Giants', 'Seattle Mariners',
            'St. Louis Cardinals', 'Tampa Bay Rays', 'Texas Rangers', 'Toronto Blue Jays', 'Washington Nationals'
        },
        'NHL': {
            'Anaheim Ducks', 'Arizona Coyotes', 'Boston Bruins', 'Buffalo Sabres', 'Calgary Flames',
            'Carolina Hurricanes', 'Chicago Blackhawks', 'Colorado Avalanche', 'Columbus Blue Jackets', 'Dallas Stars',
            'Detroit Red Wings', 'Edmonton Oilers', 'Florida Panthers', 'Los Angeles Kings', 'Minnesota Wild',
            'Montreal Canadiens', 'Nashville Predators', 'New Jersey Devils', 'New York Islanders', 'New York Rangers',
            'Ottawa Senators', 'Philadelphia Flyers', 'Pittsburgh Penguins', 'San Jose Sharks', 'Seattle Kraken',
            'St. Louis Blues', 'Tampa Bay Lightning', 'Toronto Maple Leafs', 'Vancouver Canucks', 'Vegas Golden Knights',
            'Washington Capitals', 'Winnipeg Jets'
        }
    }
    
    # Return all teams for the given sport, or an empty list if sport not found
    return list(sports_teams.get(sport, set()))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    sport = request.form.get('sport', '')
    
    if not url:
        return jsonify({"error": "No URL provided"})
        
    if not is_valid_url(url):
        return jsonify({"error": "Invalid URL provided"})
        
    # Get Game Times from ESPN for this sport - for countdown timers
    game_times = get_game_times(sport) if sport else {}
    
    # Get URLs from the provided page
    result = get_all_urls(url)
    
    if isinstance(result, dict) and "error" in result:
        return jsonify(result)
        
    return jsonify({"urls": result, "game_times": game_times})

@app.route('/debug_times/<sport>', methods=['GET'])
def debug_times(sport):
    """Debug endpoint to view game times for a specific sport."""
    if sport not in ['NBA', 'NFL', 'MLB', 'NHL']:
        return jsonify({"error": "Invalid sport. Choose from NBA, NFL, MLB, or NHL."})
        
    game_times = get_game_times(sport)
    
    # Remove the team_games index for cleaner output
    if 'team_games' in game_times:
        del game_times['team_games']
    
    return jsonify({"game_times": game_times})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 