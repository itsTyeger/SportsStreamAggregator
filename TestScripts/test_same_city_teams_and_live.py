from app import get_game_times, get_official_team_name
from datetime import datetime
import json

def test_same_city_teams_and_live():
    """Test to verify that teams from the same city (like Yankees vs Mets) can play each other
    and that live games are properly identified."""
    print(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # MLB has several same-city teams to test
    sport = 'MLB'
    print(f"\n{'='*80}")
    print(f"Testing {sport} for same-city team handling and live game detection:")
    print(f"{'='*80}")
    
    # First, verify that our team name normalization works correctly for same-city teams
    print("\nChecking team name normalization for same-city teams:")
    
    same_city_teams = [
        # New York teams
        ('New York Yankees', 'New York Mets'),
        ('NY Yankees', 'NY Mets'),
        ('NYY', 'NYM'),
        ('New York', 'New York'),  # Should be differentiated by context
        # Los Angeles teams
        ('Los Angeles Angels', 'Los Angeles Dodgers'),
        ('LA Angels', 'LA Dodgers'),
        ('LAA', 'LAD'),
        ('Los Angeles', 'Los Angeles'),  # Should be differentiated by context
        # Chicago teams
        ('Chicago Cubs', 'Chicago White Sox'),
        ('CHC', 'CWS'),
        ('Chicago', 'Chicago'),  # Should be differentiated by context
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
    
    # Now get game times and check how live games are handled
    print("\nChecking game schedule for live games:")
    
    game_times = get_game_times(sport)
    
    # Save the game times to a file for inspection
    with open('game_times_debug.json', 'w') as f:
        json.dump(game_times, f, indent=2)
    
    print(f"Saved game_times to 'game_times_debug.json' for inspection")
    
    # Check if we got any games
    if not game_times:
        print(f"No games found for {sport}")
        return
    
    # Remove metadata keys
    game_keys = [k for k in game_times.keys() if not k.startswith('_') and k != 'team_games']
    
    # Look for live games in the game times
    live_games_found = []
    
    for key in game_keys:
        game_info = game_times[key]
        if game_info.get('status') == 'live':
            matchup = game_info.get('matchup', 'Unknown matchup')
            if matchup not in [g.get('matchup') for g in live_games_found]:
                live_games_found.append(game_info)
                print(f"Found LIVE game: {matchup}")
    
    if not live_games_found:
        print("No live games found in today's schedule.")
    else:
        print(f"Found {len(live_games_found)} live games!")
        
    # Look for same-city matchups
    same_city_matchups_found = []
    
    city_team_map = {
        'new york': ['New York Yankees', 'New York Mets'],
        'los angeles': ['Los Angeles Angels', 'Los Angeles Dodgers'],
        'chicago': ['Chicago Cubs', 'Chicago White Sox'],
    }
    
    for key in game_keys:
        game_info = game_times[key]
        if 'teams' not in game_info:
            continue
            
        team1 = game_info['teams'].get('team1', '')
        team2 = game_info['teams'].get('team2', '')
        
        if not team1 or not team2:
            continue
        
        # Extract city names
        team1_parts = team1.split()
        team2_parts = team2.split()
        
        if len(team1_parts) >= 2 and len(team2_parts) >= 2:
            city1 = ' '.join(team1_parts[:-1]).lower()
            city2 = ' '.join(team2_parts[:-1]).lower()
            
            # Check if both teams are from the same city and are different teams
            if city1 == city2 and team1.lower() != team2.lower():
                matchup = f"{team1} vs {team2}"
                if matchup not in [g.get('matchup') for g in same_city_matchups_found]:
                    same_city_matchups_found.append(game_info)
                    status = "LIVE" if game_info.get('status') == 'live' else game_info.get('start_time', 'Unknown time')
                    print(f"Found same-city matchup: {matchup} - Status: {status}")
    
    if not same_city_matchups_found:
        print("No same-city matchups found in today's schedule.")
    else:
        print(f"Found {len(same_city_matchups_found)} same-city matchups!")
    
if __name__ == "__main__":
    test_same_city_teams_and_live() 