from app import get_game_times, get_official_team_name, get_all_teams_for_sport
from datetime import datetime
import json
import re

def simulate_team_extraction():
    """Test the extraction of team codes from HTML and team differentiation."""
    print(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Sample team link HTML from ESPN
    sample_links = [
        '<a href="https://www.espn.com/mlb/team/_/name/chc/chicago-cubs" class="AnchorLink">Chicago</a>',
        '<a href="https://www.espn.com/mlb/team/_/name/chw/chicago-white-sox" class="AnchorLink">Chicago</a>',
        '<a href="https://www.espn.com/mlb/team/_/name/nyy/new-york-yankees" class="AnchorLink">New York</a>',
        '<a href="https://www.espn.com/mlb/team/_/name/nym/new-york-mets" class="AnchorLink">New York</a>',
        '<a href="https://www.espn.com/mlb/team/_/name/laa/los-angeles-angels" class="AnchorLink">Los Angeles</a>',
        '<a href="https://www.espn.com/mlb/team/_/name/lad/los-angeles-dodgers" class="AnchorLink">Los Angeles</a>',
    ]
    
    # Test link extraction
    print("\nTesting team code extraction from links:")
    for link_html in sample_links:
        # Extract team code pattern similar to how the app does it
        team_code = None
        if '/team/' in link_html and '/name/' in link_html:
            parts = link_html.split('/name/')
            if len(parts) > 1:
                code_parts = parts[1].split('/')
                if len(code_parts) > 0:
                    team_code = code_parts[0].lower()
        
        # Extract team name from link text
        team_name = None
        match = re.search(r'>([^<]+)<', link_html)
        if match:
            team_name = match.group(1)
            
        print(f"Team: {team_name}, Code: {team_code}")
        
        # Try to determine full team name from code
        if team_code:
            city_part = team_name  # Usually the city name like "Chicago" or "New York"
            
            # MLB team code mappings
            suffixes = {
                'chc': 'Cubs', 'chw': 'White Sox', 'cws': 'White Sox',
                'nyy': 'Yankees', 'nym': 'Mets',
                'laa': 'Angels', 'lad': 'Dodgers',
                'sf': 'Giants', 'oak': 'Athletics',
            }
            
            if team_code in suffixes:
                full_name = f"{city_part} {suffixes[team_code]}"
                print(f"  → Generated full name: {full_name}")
                
                # Verify against official names
                official_name = get_official_team_name('MLB', full_name)
                print(f"  → Official name: {official_name}")
            
    # Test team differentiation from codes
    print("\nTesting same-city team differentiation:")
    same_city_pairs = [
        ('Chicago', 'Chicago', 'chc', 'chw', 'MLB'),
        ('New York', 'New York', 'nyy', 'nym', 'MLB'),
        ('Los Angeles', 'Los Angeles', 'laa', 'lad', 'MLB'),
    ]
    
    for (team1, team2, code1, code2, sport) in same_city_pairs:
        team1_official = get_official_team_name(sport, team1)
        team2_official = get_official_team_name(sport, team2)
        
        print(f"\nBefore differentiation:")
        print(f"{team1} ({code1}) → {team1_official}")
        print(f"{team2} ({code2}) → {team2_official}")
        
        # Simulate differentiation logic
        if team1_official.lower() == team2_official.lower() and code1 and code2 and code1 != code2:
            city_part = " ".join(team1_official.split()[:-1]) if ' ' in team1_official else team1_official
            
            # Sport-specific code mappings
            if sport == 'MLB':
                suffixes = {
                    'chc': 'Cubs', 'chw': 'White Sox', 'cws': 'White Sox',
                    'nyy': 'Yankees', 'nym': 'Mets',
                    'laa': 'Angels', 'lad': 'Dodgers',
                }
                
                if code1 in suffixes:
                    team1_official = f"{city_part} {suffixes[code1]}"
                
                if code2 in suffixes:
                    team2_official = f"{city_part} {suffixes[code2]}"
            
            print(f"\nAfter differentiation:")
            print(f"{team1} ({code1}) → {team1_official}")
            print(f"{team2} ({code2}) → {team2_official}")
            
            if team1_official.lower() != team2_official.lower():
                print("SUCCESS: Teams correctly differentiated!")
            else:
                print("ERROR: Teams still have the same name after differentiation.")
        else:
            if team1_official.lower() != team2_official.lower():
                print("Teams already differentiated by get_official_team_name")
            else:
                print("ERROR: Teams have same official name but couldn't be differentiated by codes.")
    
if __name__ == "__main__":
    simulate_team_extraction() 