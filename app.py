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
        
        # Get today's date
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        # Find the date container
        date_container = soup.find('h2', class_='Table__Title')
        if date_container:
            date_text = date_container.text.strip()
            try:
                # Parse the date from format like "Monday, May 16, 2025"
                current_date = datetime.strptime(date_text, '%A, %B %d, %Y')
            except ValueError:
                # If date parsing fails, use today's date
                current_date = datetime.now()
        else:
            current_date = datetime.now()
        
        # Find all game rows
        game_tables = soup.find_all('div', class_='ResponsiveTable')
        
        for table in game_tables:
            # Get all game rows - this varies slightly by sport
            game_rows = table.find_all('tr', class_=lambda x: x and 'Table__TR' in x)
            
            for row in game_rows:
                try:
                    # Skip header rows
                    if row.find('th'):
                        continue
                        
                    # Get teams - structure is similar across ESPN schedules but may have slight differences
                    team_cells = row.find_all('td', class_='Table__TD')
                    if len(team_cells) < 3:
                        continue
                    
                    # Try different ways to find the teams based on ESPN's layout for different sports
                    team_links = []
                    
                    # First attempt - looking in the first cell for two team links
                    if len(team_cells) > 0:
                        team_links = team_cells[0].find_all('a', class_='AnchorLink')
                        
                    # Second attempt - some sports have teams in different cells
                    if len(team_links) < 2 and len(team_cells) >= 2:
                        home_team = team_cells[0].find('a', class_='AnchorLink')
                        away_team = team_cells[1].find('a', class_='AnchorLink')
                        if home_team and away_team:
                            team_links = [home_team, away_team]
                    
                    # If we still don't have teams, try to find spans with team names
                    if len(team_links) < 2:
                        team_spans = row.find_all('span', class_=lambda x: x and ('TeamName' in x or 'abbr' in x))
                        if len(team_spans) >= 2:
                            team1 = team_spans[0].text.strip()
                            team2 = team_spans[1].text.strip()
                        else:
                            continue
                    else:
                        team1 = team_links[0].text.strip()
                        team2 = team_links[1].text.strip()
                    
                    # Get official team names from our dictionary
                    team1_official = get_official_team_name(sport, team1)
                    team2_official = get_official_team_name(sport, team2)
                    
                    # Get game time - look for time in different possible cells
                    time_cell = None
                    # Look for game time in different cells - varies by sport
                    for cell in team_cells:
                        cell_text = cell.text.strip()
                        if ':' in cell_text or 'LIVE' in cell_text or 'PM' in cell_text or 'AM' in cell_text:
                            time_cell = cell
                            break
                    
                    if not time_cell:
                        continue
                        
                    time_text = time_cell.text.strip()
                    
                    # Check if game is final, in progress, or scheduled
                    game_status = "upcoming"
                    if "LIVE" in time_text or ":" in time_text:
                        game_status = "upcoming" 
                    elif "FINAL" in time_text or "F/" in time_text:
                        # Skip games that are already finished
                        continue
                        
                    if "LIVE" in time_text:
                        # Game is live, set time to now
                        game_time = datetime.now()
                    elif ":" in time_text and ("ET" in time_text or "PM" in time_text or "AM" in time_text):
                        # Regular time format
                        time_parts = time_text.replace('ET', '').strip()
                        try:
                            # Try different time formats
                            try:
                                game_time = datetime.strptime(time_parts, '%I:%M %p')
                            except ValueError:
                                try:
                                    game_time = datetime.strptime(time_parts, '%H:%M')
                                except ValueError:
                                    continue
                            
                            # Add date components
                            game_time = game_time.replace(
                                year=current_date.year,
                                month=current_date.month,
                                day=current_date.day
                            )
                            
                            # Convert to user's local time
                            et_tz = pytz.timezone('US/Eastern')
                            game_time = et_tz.localize(game_time)
                            
                            # Matchup formats: both the original ESPN format and our standardized format
                            espn_matchup = f"{team1} vs {team2}"
                            std_matchup = f"{team1_official} vs {team2_official}"
                            
                            # Store game info including status and formatted time
                            time_info = {
                                'utc_time': game_time.astimezone(pytz.UTC).isoformat(),
                                'local_time': game_time.strftime('%I:%M %p %Z'),
                                'status': game_status
                            }
                            
                            # Store under both matchup formats to maximize chance of matching
                            game_times[espn_matchup] = time_info
                            game_times[std_matchup] = time_info
                            
                            # Also try in reverse order since some sites might list away vs home instead
                            rev_espn_matchup = f"{team2} vs {team1}"
                            rev_std_matchup = f"{team2_official} vs {team1_official}"
                            game_times[rev_espn_matchup] = time_info
                            game_times[rev_std_matchup] = time_info
                            
                        except ValueError as e:
                            print(f"Time parsing error: {e} for {time_text}")
                            continue
                except Exception as e:
                    print(f"Error parsing game row: {e}")
                    continue
                
        print(f"Found {len(game_times)} game times for {sport}")
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
        # 1. Check for abbreviation first (exact match only)
        if sport in espn_abbreviations and team_name_clean in espn_abbreviations[sport]:
            return espn_abbreviations[sport][team_name_clean]
        
        # 2. Try exact match
        for official_name in sports_teams[sport]:
            if official_name.lower() == team_name_lower:
                return official_name
        
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    selected_sport = request.form.get('sport', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        urls = get_all_urls(url)
        if isinstance(urls, dict) and 'error' in urls:
            return jsonify({'error': urls['error']}), 400
            
        # Get game times for the selected sport
        game_times = {}
        if selected_sport in ['NBA', 'NFL', 'MLB', 'NHL']:
            game_times = get_game_times(selected_sport)
            
        if selected_sport:
            urls = [(url, title) for url, title in urls if title.startswith(selected_sport + ':')]
            
        return jsonify({
            'urls': urls,
            'game_times': game_times
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 