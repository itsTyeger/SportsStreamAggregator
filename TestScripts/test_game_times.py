from app import get_game_times
from datetime import datetime

def test_game_times():
    """Test the get_game_times function to verify it's correctly filtering by date."""
    print(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Test all supported sports
    sports = ['NBA', 'NHL', 'MLB', 'NFL']
    
    for sport in sports:
        print(f"\n{'='*80}")
        print(f"Testing {sport} schedule:")
        print(f"{'='*80}")
        
        # Get game times for this sport
        game_times = get_game_times(sport)
        
        # Check if we got any games
        if not game_times:
            print(f"No games found for {sport}")
            continue
        
        # Remove metadata keys
        game_keys = [k for k in game_times.keys() if not k.startswith('_') and k != 'team_games']
        
        print(f"Found {len(game_keys) // 2} games for {sport}") # Divide by 2 because each game has two entries (home/away)
        
        # Print details of each game
        games_by_id = {}
        for key in game_keys:
            game_info = game_times[key]
            game_id = game_info['game_id']
            
            # Only process each game once
            if game_id in games_by_id:
                continue
                
            games_by_id[game_id] = game_info
            
            # Print game details
            print(f"Game: {game_info['matchup']}")
            print(f"  Date: {game_info['game_date']} (Section Date: {game_info['section_date']})")
            print(f"  Time: {game_info['start_time']} {game_info['status']}")
            print(f"  Teams: {game_info['teams']['team1']} vs {game_info['teams']['team2']}")
            print()

if __name__ == "__main__":
    test_game_times() 