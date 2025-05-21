from datetime import datetime
import pytz

def process_live_game(
    sport, team1, team2, team1_official, team2_official,
    game_id, row_position, table_idx, section_date,
    team1_key, team2_key, teams_with_games_today, processed_game_ids,
    game_times
):
    """Process a live game and add it to game_times."""
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
        'status': 'live',
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
        normalized = normalized.replace('fc', '').replace('team', '')
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace()).strip()
        
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
    
    return game_times 