from flask import render_template, request, jsonify
from ..utils import is_valid_url
from ..scraper import get_all_urls, get_game_times

def configure_routes(app):
    """Configure the routes for the Flask application."""
    
    @app.route('/')
    def home():
        """Render the home page."""
        return render_template('index.html')
    
    @app.route('/scrape', methods=['POST'])
    def scrape():
        """Scrape URLs from a given website."""
        url = request.form.get('url')
        sport = request.form.get('sport', '')
        
        if not url:
            return jsonify({"error": "No URL provided"})
            
        if not is_valid_url(url):
            return jsonify({"error": "Invalid URL provided"})
            
        # Get Game Times from ESPN for this sport - for countdown timers
        game_times = get_game_times(sport) if sport else {}
        
        # Get URLs from the provided page
        result = get_all_urls(url)
        
        if isinstance(result, dict) and "error" in result:
            return jsonify(result)
            
        return jsonify({"urls": result, "game_times": game_times})
    
    @app.route('/debug_times/<sport>', methods=['GET'])
    def debug_times(sport):
        """Debug endpoint to view game times for a specific sport."""
        if sport not in ['NBA', 'NFL', 'MLB', 'NHL']:
            return jsonify({"error": "Invalid sport. Choose from NBA, NFL, MLB, or NHL."})
            
        game_times = get_game_times(sport)
        
        # Remove the team_games index for cleaner output
        if 'team_games' in game_times:
            del game_times['team_games']
        
        return jsonify({"game_times": game_times})
    
    @app.route('/debug_mlb_completed', methods=['GET'])
    def debug_mlb_completed():
        """Debug endpoint specifically for MLB completed games."""
        game_times = get_game_times("MLB")
        
        # Filter to only include completed MLB games
        completed_games = {}
        
        for key, value in game_times.items():
            if isinstance(value, dict) and value.get('status') == 'completed':
                completed_games[key] = value
        
        # Add metadata
        if '_meta' in game_times:
            completed_games['_meta'] = game_times['_meta']
            completed_games['_meta']['completed_count'] = len(completed_games) - 1  # Subtract 1 for _meta
        
        return jsonify({
            "completed_games": completed_games,
            "count": len(completed_games) - (1 if '_meta' in completed_games else 0)
        })
        
    @app.route('/mlb_scores', methods=['GET'])
    def mlb_scores():
        """Simplified endpoint that displays MLB completed games in a clean format."""
        print("Fetching MLB scores...")
        game_times = get_game_times("MLB")
        
        # Format the results specifically for display
        completed_games = []
        
        for key, value in game_times.items():
            if isinstance(value, dict) and value.get('status') == 'completed':
                # Extract the team names and scores from the data
                teams = value.get('teams', {})
                team1 = teams.get('team1', 'Unknown Team')
                team2 = teams.get('team2', 'Unknown Team')
                
                # Extract result which should be in format like "3-2" or "Postponed"
                result = value.get('result', 'No Score')
                
                # Log for debugging
                print(f"Found completed MLB game: {team1} vs {team2}, Result: {result}")
                
                # Add to our formatted results
                completed_games.append({
                    'matchup': f"{team1} vs {team2}",
                    'score': result,
                    'game_date': value.get('game_date', 'Unknown Date')
                })
        
        print(f"Total MLB completed games found: {len(completed_games)}")
        
        # For additional debugging, log all keys in the game_times dictionary
        all_keys = list(game_times.keys())
        print(f"All keys in game_times: {all_keys[:10]}...")  # Show first 10 keys
        
        # Look for postponed game entries specifically
        postponed_games = []
        for key, value in game_times.items():
            if isinstance(value, dict) and isinstance(value.get('result'), str) and 'postponed' in value.get('result', '').lower():
                teams = value.get('teams', {})
                team1 = teams.get('team1', 'Unknown Team')
                team2 = teams.get('team2', 'Unknown Team')
                print(f"Found postponed game: {team1} vs {team2}")
                postponed_games.append({
                    'matchup': f"{team1} vs {team2}",
                    'status': value.get('result', 'Postponed'),
                })
        
        return jsonify({
            "mlb_completed_games": completed_games,
            "postponed_games": postponed_games,
            "count": len(completed_games),
            "postponed_count": len(postponed_games)
        }) 