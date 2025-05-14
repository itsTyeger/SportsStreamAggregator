from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

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

        # Create variations of team names for better matching
        team_variations = {}
        for sport, teams in sports_teams.items():
            for team in teams:
                # Full name
                team_variations[team.lower()] = (team, sport)
                # City name
                city = team.split()[0].lower()
                team_variations[city] = (team, sport)
                # Team name without city
                team_name = ' '.join(team.split()[1:]).lower()
                team_variations[team_name] = (team, sport)

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
            
            # Combine text for searching
            search_text = (text + ' ' + href).lower()
            
            # Find teams in the text
            found_teams = {}
            for variation, (full_name, sport) in team_variations.items():
                if variation in search_text:
                    if sport not in found_teams:
                        found_teams[sport] = set()
                    found_teams[sport].add(full_name)
            
            # Process each sport
            for sport, teams in found_teams.items():
                if len(teams) >= 2:
                    # Take the first two teams found
                    teams_list = sorted(list(teams))[:2]
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    selected_sport = request.form.get('sport', '')
    
    if not url:
        # Return a clear error if no URL is provided
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        urls = get_all_urls(url)
        # If get_all_urls returns an error dict, return it as a JSON error
        if isinstance(urls, dict) and 'error' in urls:
            return jsonify({'error': urls['error']}), 400
        if selected_sport:
            # Filter URLs for the selected sport
            urls = [(url, title) for url, title in urls if title.startswith(selected_sport + ':')]
        return jsonify({'urls': urls})
    except Exception as e:
        # Return any other error as a JSON error
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 