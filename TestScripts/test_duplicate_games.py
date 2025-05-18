from app import get_game_times
from datetime import datetime

def test_for_duplicate_games():
    """Test to check if the get_game_times function correctly prevents duplicate games."""
    print(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Test all supported sports
    sports = ['MLB', 'NBA', 'NHL', 'NFL']
    
    for sport in sports:
        print(f"\n{'='*80}")
        print(f"Testing {sport} schedule for duplicate detection:")
        print(f"{'='*80}")
        
        # Get game times for this sport
        game_times = get_game_times(sport)
        
        # Check if we got any games
        if not game_times:
            print(f"No games found for {sport}")
            continue
        
        # Remove metadata keys
        game_keys = [k for k in game_times.keys() if not k.startswith('_') and k != 'team_games']
        
        print(f"Found {len(game_keys)} game entries")
        
        # Check for duplicate games (same teams playing each other more than once on same day)
        games_by_team_pair = {}
        duplicate_team_errors = 0
        
        for key in game_keys:
            game_info = game_times[key]
            game_id = game_info['game_id']
            
            # Create a key with teams in any order
            team1 = game_info['teams']['team1'].lower()
            team2 = game_info['teams']['team2'].lower()
            
            # Check for duplicate team error (same team on both sides)
            if team1 == team2:
                print(f"ERROR: Same team on both sides: {team1} vs {team2}")
                duplicate_team_errors += 1
            
            team_pair = tuple(sorted([team1, team2]))
            
            # Track by team pair for duplicate detection
            if team_pair not in games_by_team_pair:
                games_by_team_pair[team_pair] = []
            games_by_team_pair[team_pair].append(game_id)
        
        # Report duplicates by team pair
        print("\nChecking for duplicate team pairs:")
        team_duplicate_count = 0
        for team_pair, game_ids in games_by_team_pair.items():
            # Because we store each game twice (home/away perspective), we expect 2 entries per unique game
            # So we divide by 2 to get the true count of unique games for this team pair
            unique_games = len(set(game_ids)) / 2
            
            # If there's more than 1 unique game for this team pair, it's a duplicate
            if unique_games > 1:
                print(f"  Duplicate team pair: {team_pair[0]} vs {team_pair[1]} - {len(game_ids)} entries, {unique_games} unique games")
                team_duplicate_count += 1
        
        if team_duplicate_count == 0:
            print("  No duplicate team pairs found!")
            
        if duplicate_team_errors == 0:
            print("  No teams playing against themselves found!")
        else:
            print(f"  ERROR: Found {duplicate_team_errors} teams playing against themselves!")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_for_duplicate_games() 