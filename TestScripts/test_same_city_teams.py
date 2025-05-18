from app import get_game_times, get_official_team_name
from datetime import datetime

def test_same_city_teams():
    """Test to verify that teams from the same city (like LA Dodgers vs LA Angels) can play each other."""
    print(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # MLB has several same-city teams to test
    sport = 'MLB'
    print(f"\n{'='*80}")
    print(f"Testing {sport} for same-city team handling:")
    print(f"{'='*80}")
    
    # First, verify that our team name normalization works correctly for same-city teams
    print("\nChecking team name normalization for same-city teams:")
    
    same_city_teams = [
        # Los Angeles teams
        ('Los Angeles Angels', 'Los Angeles Dodgers'),
        ('LA Angels', 'LA Dodgers'),
        # New York teams
        ('New York Yankees', 'New York Mets'),
        ('NY Yankees', 'NY Mets'),
        # Chicago teams
        ('Chicago Cubs', 'Chicago White Sox'),
        ('CHC', 'CWS'),
    ]
    
    for team1, team2 in same_city_teams:
        team1_official = get_official_team_name(sport, team1)
        team2_official = get_official_team_name(sport, team2)
        
        print(f"{team1} -> {team1_official}")
        print(f"{team2} -> {team2_official}")
        
        # Verify they're different after normalization
        if team1_official.lower() == team2_official.lower():
            print(f"ERROR: Teams normalized to same name: {team1_official}")
        else:
            print(f"SUCCESS: Teams correctly remain distinct after normalization")
        print()
    
    # Now get game times and check if LA teams can play each other
    print("\nChecking game schedule for same-city matchups:")
    
    game_times = get_game_times(sport)
    
    # Check if we got any games
    if not game_times:
        print(f"No games found for {sport}")
        return
    
    # Remove metadata keys
    game_keys = [k for k in game_times.keys() if not k.startswith('_') and k != 'team_games']
    
    # Look for same-city matchups in the game times
    same_city_matchups_found = []
    
    city_team_map = {
        'los angeles': ['Los Angeles Angels', 'Los Angeles Dodgers'],
        'new york': ['New York Yankees', 'New York Mets'],
        'chicago': ['Chicago Cubs', 'Chicago White Sox'],
    }
    
    for key in game_keys:
        game_info = game_times[key]
        team1 = game_info['teams']['team1']
        team2 = game_info['teams']['team2']
        
        # Extract city names
        team1_parts = team1.split()
        team2_parts = team2.split()
        
        if len(team1_parts) >= 2 and len(team2_parts) >= 2:
            city1 = ' '.join(team1_parts[:-1]).lower()
            city2 = ' '.join(team2_parts[:-1]).lower()
            
            # Check if both teams are from the same city and are different teams
            if city1 == city2 and team1.lower() != team2.lower():
                matchup = f"{team1} vs {team2}"
                if matchup not in same_city_matchups_found:
                    same_city_matchups_found.append(matchup)
                    print(f"Found same-city matchup: {matchup} at {game_info['start_time']}")
    
    if not same_city_matchups_found:
        print("No same-city matchups found in today's schedule.")
        
        # Create a simulated matchup for LA teams to check our normalization
        la_matchup = "Los Angeles Angels vs Los Angeles Dodgers"
        print(f"\nSimulating matchup: {la_matchup}")
        
        team1 = "Los Angeles Angels"
        team2 = "Los Angeles Dodgers"
        team1_official = get_official_team_name(sport, team1)
        team2_official = get_official_team_name(sport, team2)
        
        # Check that our duplicate detection would allow this matchup
        team1_key = team1_official.lower()
        team2_key = team2_official.lower()
        
        print(f"Team1 key: {team1_key}")
        print(f"Team2 key: {team2_key}")
        
        # A valid matchup should have different official team names
        if team1_official.lower() != team2_official.lower():
            print(f"SUCCESS: {team1} and {team2} are correctly identified as different teams")
        else:
            print(f"ERROR: {team1} and {team2} are incorrectly normalized to the same team")
    
if __name__ == "__main__":
    test_same_city_teams() 