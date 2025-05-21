import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

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