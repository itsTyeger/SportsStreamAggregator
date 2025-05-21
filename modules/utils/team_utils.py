# Dictionary of sports and their teams
SPORTS_TEAMS = {
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
ESPN_ABBREVIATIONS = {
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
        'CHW': 'Chicago White Sox',
        'NYY': 'New York Yankees',
        'NYM': 'New York Mets',
        'STL': 'St. Louis Cardinals',
        'KC': 'Kansas City Royals',
        'TB': 'Tampa Bay Rays',
        'LAD': 'Los Angeles Dodgers',
        'LA': 'Los Angeles Dodgers',
        'LAA': 'Los Angeles Angels',
        'TOR': 'Toronto Blue Jays',
        'DET': 'Detroit Tigers',
        'TBR': 'Tampa Bay Rays',
        'BOS': 'Boston Red Sox',
        'BAL': 'Baltimore Orioles',
        'OAK': 'Oakland Athletics',
        'SEA': 'Seattle Mariners',
        'HOU': 'Houston Astros',
        'ARI': 'Arizona Diamondbacks',
        'ATL': 'Atlanta Braves',
        'MIA': 'Miami Marlins',
        'PHI': 'Philadelphia Phillies',
        'WSH': 'Washington Nationals',
        'CIN': 'Cincinnati Reds',
        'PIT': 'Pittsburgh Pirates',
        'MIL': 'Milwaukee Brewers',
        'COL': 'Colorado Rockies',
        'CLE': 'Cleveland Guardians',
        'MIN': 'Minnesota Twins',
        'TEX': 'Texas Rangers'
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

def get_official_team_name(sport, team_name):
    """Get the official team name from our dictionary of teams with improved matching."""
    if not team_name:
        return team_name
        
    # Clean input
    team_name_clean = team_name.strip()
    team_name_lower = team_name_clean.lower()
    
    # Special handling for MLB team abbreviations - check this first
    if sport == 'MLB':
        # Check for direct abbreviation matches (case insensitive)
        for abbr, full_name in ESPN_ABBREVIATIONS['MLB'].items():
            if team_name_clean.upper() == abbr:
                print(f"Matched MLB abbreviation: {abbr} -> {full_name}")
                return full_name
        
        # Special handling for Toronto Blue Jays
        if 'tor' in team_name_lower or 'blue j' in team_name_lower or 'jays' in team_name_lower:
            return 'Toronto Blue Jays'
            
        # Special handling for Detroit Tigers
        if 'det' in team_name_lower or 'tiger' in team_name_lower:
            return 'Detroit Tigers'
    
    # Try to find the best match
    if sport in SPORTS_TEAMS:
        # First check for same-city teams using identifiable keywords
        
        # Special handling for New York teams (Yankees/Mets)
        if sport == 'MLB' and team_name_lower in ['new york', 'ny']:
            print(f"Handling New York MLB team: '{team_name}'")
            # Try to use more context to determine which NY team
            if 'yankee' in team_name_lower or 'nyy' in team_name_lower or 'yanks' in team_name_lower:
                return 'New York Yankees'
            elif 'met' in team_name_lower or 'nym' in team_name_lower or 'mets' in team_name_lower:
                return 'New York Mets'
            # Default to Yankees for now if no clear indicators
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
        if sport in ESPN_ABBREVIATIONS and team_name_clean in ESPN_ABBREVIATIONS[sport]:
            return ESPN_ABBREVIATIONS[sport][team_name_clean]
        
        # 2. Try exact match
        for official_name in SPORTS_TEAMS[sport]:
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
        for official_name in SPORTS_TEAMS[sport]:
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
        
        for official_name in SPORTS_TEAMS[sport]:
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
    # Return all teams for the given sport, or an empty list if sport not found
    return list(SPORTS_TEAMS.get(sport, set())) 