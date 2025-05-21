import re
from datetime import datetime
import pytz
from ...utils.team_utils import get_official_team_name

def process_game_row(sport, row, team_cells, game_id, row_position, table_idx, section_date, teams_with_games_today, processed_game_ids, game_times):
    """Process a single game row and extract game information."""
    # Try multiple approaches to find teams
    team1 = None
    team2 = None
    
    # Check for postponed games first - they're usually easy to identify
    is_postponed = False
    result_text = None
    row_text = row.text.strip().upper()
    if "POSTPONED" in row_text or "PPD" in row_text:
        is_postponed = True
        result_text = "Postponed"
        print(f"Found a POSTPONED game in row: {row_text[:50]}...")
    
    # Extra logging for MLB games
    is_mlb = sport == 'MLB'
    if is_mlb:
        print(f"\n=== PROCESSING MLB ROW ===")
        
        # For MLB, check if this is a "FINAL" row or "POSTPONED" row
        row_contains_final = "FINAL" in row_text
        if row_contains_final:
            print(f"  Found FINAL indicator in MLB row")
        if is_postponed:
            print(f"  Found POSTPONED indicator in MLB row")
            
        # Print first few cells to help with debugging
        first_few_cells = row.find_all('td', class_='Table__TD')[:5]
        for i, cell in enumerate(first_few_cells):
            print(f"  MLB Cell {i}: {cell.text.strip()}")
    
    # First attempt - find all team links across all cells
    all_team_links = row.find_all('a', class_='AnchorLink')
    team_links = [link for link in all_team_links if link.find('abbr') or '/team/' in link.get('href', '') or 'gamecast' not in link.get('href', '')]
    
    if len(team_links) >= 2:
        # Extract more detailed team info from href if possible
        team1 = team_links[0].text.strip()
        team2 = team_links[1].text.strip()
        
        # Check if we have links with team codes (particularly useful for same-city teams)
        href1 = team_links[0].get('href', '')
        href2 = team_links[1].get('href', '')
        
        # Extract team codes from hrefs (e.g. "laa" from "/mlb/team/_/name/laa/los-angeles-angels")
        team1_code = None
        team2_code = None
        
        if '/team/' in href1 and '/name/' in href1:
            parts = href1.split('/name/')
            if len(parts) > 1:
                code_parts = parts[1].split('/')
                if len(code_parts) > 0:
                    team1_code = code_parts[0]
        
        if '/team/' in href2 and '/name/' in href2:
            parts = href2.split('/name/')
            if len(parts) > 1:
                code_parts = parts[1].split('/')
                if len(code_parts) > 0:
                    team2_code = code_parts[0]
        
        # Special handling for Los Angeles teams using team codes
        if team1 == 'Los Angeles' and team2 == 'Los Angeles' and team1_code and team2_code:
            if team1_code.lower() == 'laa' and team2_code.lower() == 'lad':
                team1 = 'Los Angeles Angels'
                team2 = 'Los Angeles Dodgers'
                print(f"Fixed LA teams using codes: {team1} vs {team2}")
            elif team1_code.lower() == 'lad' and team2_code.lower() == 'laa':
                team1 = 'Los Angeles Dodgers'
                team2 = 'Los Angeles Angels'
                print(f"Fixed LA teams using codes: {team1} vs {team2}")
                
        # Special handling for New York teams using team codes
        if team1 == 'New York' and team2 == 'New York' and team1_code and team2_code:
            if team1_code.lower() == 'nym' and team2_code.lower() == 'nyy':
                team1 = 'New York Mets'
                team2 = 'New York Yankees'
                print(f"Fixed NY teams using codes: {team1} vs {team2}")
            elif team1_code.lower() == 'nyy' and team2_code.lower() == 'nym':
                team1 = 'New York Yankees'
                team2 = 'New York Mets'
                print(f"Fixed NY teams using codes: {team1} vs {team2}")
                
        # Special handling for Chicago teams using team codes
        if team1 == 'Chicago' and team2 == 'Chicago' and team1_code and team2_code:
            print(f"Differentiating Chicago teams with codes: {team1_code} vs {team2_code}")
            if (team1_code.lower() == 'chc' or team1_code.lower() == 'chi') and (team2_code.lower() == 'chw' or team2_code.lower() == 'cws'):
                team1 = 'Chicago Cubs'
                team2 = 'Chicago White Sox'
                print(f"Fixed Chicago teams using codes: {team1} vs {team2}")
            elif (team1_code.lower() == 'chw' or team1_code.lower() == 'cws') and (team2_code.lower() == 'chc' or team2_code.lower() == 'chi'):
                team1 = 'Chicago White Sox'
                team2 = 'Chicago Cubs'
                print(f"Fixed Chicago teams using codes: {team1} vs {team2}")
    
    # Special MLB-specific parsing if we couldn't find teams or this is MLB
    if (not team1 or not team2) and is_mlb:
        print("  Trying MLB-specific team detection...")
        # Try to find team logos which often contain the team name in alt text or class
        team_logos = row.find_all('img', class_=lambda x: x and ('logo' in x.lower() or 'team' in x.lower()))
        
        if len(team_logos) >= 2:
            # Check for alt text which often contains team name
            if team_logos[0].get('alt') and team_logos[1].get('alt'):
                team1 = team_logos[0].get('alt').strip()
                team2 = team_logos[1].get('alt').strip()
                print(f"  Found MLB teams from logos: {team1} vs {team2}")
        
        # If still no team names, look for team abbreviations in cell text
        if not team1 or not team2:
            for idx, cell in enumerate(team_cells[:4]):  # Check first few cells
                cell_text = cell.text.strip()
                
                # Look for match in first cells - MLB often shows abbreviations
                if idx == 0 and len(cell_text) <= 3 and cell_text.isupper():
                    team1_abbr = cell_text
                    print(f"  Found potential MLB team1 abbr: {team1_abbr}")
                    # Try to find matching team
                    for team in get_all_teams_for_sport("MLB"):
                        if team1_abbr in team:
                            team1 = team
                            print(f"  Matched MLB team1: {team1}")
                            break
                
                if idx == 1 and len(cell_text) <= 3 and cell_text.isupper():
                    team2_abbr = cell_text
                    print(f"  Found potential MLB team2 abbr: {team2_abbr}")
                    # Try to find matching team
                    for team in get_all_teams_for_sport("MLB"):
                        if team2_abbr in team:
                            team2 = team
                            print(f"  Matched MLB team2: {team2}")
                            break
                            
        # Try to extract score from cells if this is a completed game
        if team1 and team2 and any("FINAL" in c.text.upper() for c in team_cells):
            print("  Looking for MLB game score...")
            score1 = None
            score2 = None
            
            # Look for score in specific cells
            for idx, cell in enumerate(team_cells[:6]):  # Check first few cells
                cell_text = cell.text.strip()
                
                # MLB scores are typically single digits in their own cells
                if idx >= 2 and idx <= 4 and cell_text.isdigit():
                    if score1 is None:
                        score1 = cell_text
                        print(f"  Found MLB score1: {score1}")
                    elif score2 is None:
                        score2 = cell_text
                        print(f"  Found MLB score2: {score2}")
                        break
            
            # If we found both scores, store for later
            if score1 and score2:
                # Store at function level so other parts can access it
                game_result = f"{score1}-{score2}"
                print(f"  MLB GAME RESULT: {game_result}")
    
    # Second attempt - look for team name spans
    if not team1 or not team2:
        team_spans = row.find_all('span', class_=lambda x: x and ('TeamName' in x or 'abbr' in x or 'teamName' in x))
        if len(team_spans) >= 2:
            team1 = team_spans[0].text.strip()
            team2 = team_spans[1].text.strip()
    
    # Third attempt - use the first two cells if they have content
    if (not team1 or not team2) and len(team_cells) >= 2:
        # Some tables have teams in first two cells
        cell1_text = team_cells[0].text.strip()
        cell2_text = team_cells[1].text.strip()
        
        # Ensure the cells contain team names (not just numbers/times)
        if len(cell1_text) > 2 and not cell1_text[0].isdigit() and not ':' in cell1_text:
            team1 = cell1_text
        if len(cell2_text) > 2 and not cell2_text[0].isdigit() and not ':' in cell2_text:
            team2 = cell2_text
    
    # If we still don't have team names, try one last approach for specific sports
    if (not team1 or not team2) and sport in ['NBA', 'NHL']:
        # These sports often have a single cell with "Team @ Team" format
        for cell in team_cells:
            cell_text = cell.text.strip()
            if '@' in cell_text and len(cell_text.split('@')) == 2:
                teams = cell_text.split('@')
                team1 = teams[0].strip()
                team2 = teams[1].strip()
                break
    
    # If we still couldn't find teams, skip this row
    if not team1 or not team2:
        print(f"Skipping row in {sport} - could not identify teams")
        print(f"--- SKIPPED PROCESSING: Could not identify teams ---\n")
        return game_times
    
    # Clean up team names
    team1 = team1.strip()
    team2 = team2.strip()
    
    # Print detailed debug info for the Los Angeles teams
    if 'los angeles' in team1.lower() or 'los angeles' in team2.lower():
        print(f"DEBUG - Found LA team(s): '{team1}' vs '{team2}'")
        print(f"  Team1 source: {type(team1)}, length: {len(team1)}")
        print(f"  Team2 source: {type(team2)}, length: {len(team2)}")
        
        # Look for evidence of Angels vs Dodgers in the game ID or href
        angels_dodgers_found = False
        for cell in team_cells:
            cell_html = str(cell)
            if 'angels-dodgers' in cell_html:
                print(f"  Found Angels vs Dodgers in game ID!")
                team1 = "Los Angeles Angels"
                team2 = "Los Angeles Dodgers"
                angels_dodgers_found = True
                break
        
        # Print the raw HTML of the cells
        for i, cell in enumerate(team_cells[:3]):
            print(f"  Cell {i} HTML: {cell}")
        
        # If evidence found, don't continue with regular checks
        if angels_dodgers_found:
            print(f"Using identified teams: {team1} vs {team2}")

    # Check if teams are duplicates (like "Los Angeles Angels vs Los Angeles Angels")
    # Special case - if both are "Los Angeles" without specifics, check for more clues
    if team1.lower() == team2.lower():
        print(f"Skipping duplicate team matchup: {team1} vs {team2}")
        print(f"--- SKIPPED PROCESSING: Duplicate team names ---\n")
        return game_times
    
    # Get official team names from our dictionary
    team1_official = get_official_team_name(sport, team1)
    team2_official = get_official_team_name(sport, team2)
    
    # Extra debugging for Chicago teams
    if 'chicago' in team1.lower() or 'chicago' in team2.lower():
        print(f"DEBUG - Chicago team detection: '{team1}' vs '{team2}'")
        print(f"  Official names: '{team1_official}' vs '{team2_official}'")
        if 'team1_code' in locals() and team1_code:
            print(f"  Team1 code: {team1_code}")
        if 'team2_code' in locals() and team2_code:
            print(f"  Team2 code: {team2_code}")
    
    # Extract team identifiers from URLs or classes to differentiate same-city teams
    team1_code = None
    team2_code = None
    
    # Look for team codes in href attributes
    for cell in team_cells:
        cell_html = str(cell)
        # Try to extract team codes from href attributes
        for link in cell.find_all('a', href=True):
            href = link.get('href', '')
            # Look for team codes in URL (typically after /name/)
            if '/team/' in href and '/name/' in href:
                parts = href.split('/name/')
                if len(parts) > 1:
                    code_parts = parts[1].split('/')
                    if len(code_parts) > 0:
                        code = code_parts[0].lower()
                        
                        # Check if this is the first or second team's link
                        if link.text.strip().lower() == team1.lower() or team1.lower() in link.text.strip().lower():
                            team1_code = code
                            print(f"Found code for {team1}: {team1_code}")
                        elif link.text.strip().lower() == team2.lower() or team2.lower() in link.text.strip().lower():
                            team2_code = code
                            print(f"Found code for {team2}: {team2_code}")
    
    # Use team codes (if found) to distinguish between same-city teams
    if team1_official.lower() == team2_official.lower() and team1_code and team2_code and team1_code != team2_code:
        print(f"Same city teams detected with different codes: {team1_code} vs {team2_code}")
        
        # Look for team code mappings in href or row
        team_mapping = {}
        for cell in team_cells:
            cell_html = str(cell)
            
            # Check for known team codes in the entire row's HTML
            if team1_code:
                if f"/{team1_code}/" in cell_html.lower() or f"{team1_code}." in cell_html.lower():
                    for team in get_all_teams_for_sport(sport):
                        if team1_code.lower() in team.lower() or team.lower() in team1_code:
                            team_mapping[team1_code] = team
                            break
            
            if team2_code:
                if f"/{team2_code}/" in cell_html.lower() or f"{team2_code}." in cell_html.lower():
                    for team in get_all_teams_for_sport(sport):
                        if team2_code.lower() in team.lower() or team.lower() in team2_code:
                            team_mapping[team2_code] = team
                            break
        
        # Update official names if we found mappings
        if team1_code in team_mapping:
            team1_official = team_mapping[team1_code]
            print(f"Updated {team1} to {team1_official} using code {team1_code}")
        
        if team2_code in team_mapping:
            team2_official = team_mapping[team2_code]
            print(f"Updated {team2} to {team2_official} using code {team2_code}")
    
    # If team names are still the same, try to differentiate by looking at team codes
    if team1_official.lower() == team2_official.lower() and team1_code and team2_code and team1_code != team2_code:
        # Last resort - try to construct team names from city and codes
        city_part = " ".join(team1_official.split()[:-1])  # Get the city part
        
        # Try to generate names based on codes - this is a fallback approach
        sport_lowercase = sport.lower()
        if sport_lowercase == 'mlb':
            # MLB team code mappings
            suffixes = {
                'chc': 'Cubs', 'chw': 'White Sox', 'cws': 'White Sox',
                'nyy': 'Yankees', 'nym': 'Mets',
                'laa': 'Angels', 'lad': 'Dodgers',
                'sf': 'Giants', 'oak': 'Athletics',
            }
            
            if team1_code in suffixes:
                team1_official = f"{city_part} {suffixes[team1_code]}"
                print(f"Generated name for {team1}: {team1_official}")
            
            if team2_code in suffixes:
                team2_official = f"{city_part} {suffixes[team2_code]}"
                print(f"Generated name for {team2}: {team2_official}")
                
        elif sport_lowercase == 'nhl':
            # NHL codes like nyr/nyi for Rangers/Islanders
            if city_part.lower() == 'new york':
                if team1_code == 'nyr':
                    team1_official = 'New York Rangers'
                elif team1_code == 'nyi':
                    team1_official = 'New York Islanders'
                    
                if team2_code == 'nyr':
                    team2_official = 'New York Rangers'
                elif team2_code == 'nyi':
                    team2_official = 'New York Islanders'
            
            # LA Kings vs Anaheim Ducks
            elif city_part.lower() == 'los angeles':
                if team1_code == 'lak':
                    team1_official = 'Los Angeles Kings'
                elif team1_code == 'ana':
                    team1_official = 'Anaheim Ducks'
                    
                if team2_code == 'lak':
                    team2_official = 'Los Angeles Kings'
                elif team2_code == 'ana':
                    team2_official = 'Anaheim Ducks'
    
    # Check again after trying to differentiate
    if team1_official.lower() == team2_official.lower():
        print(f"Skipping duplicate team matchup (after differentiation): {team1_official} vs {team2_official}")
        print(f"--- SKIPPED PROCESSING: Duplicate official team names ---\n")
        return game_times
    
    # Create team keys based on full team name plus code if available
    team1_key = team1_official.lower()
    if team1_code:
        team1_key += f"_{team1_code}"
        
    team2_key = team2_official.lower()
    if team2_code:
        team2_key += f"_{team2_code}"
    
    # Create a matchup key for detecting exact duplicate games
    matchup_key = f"{team1_key}_{team2_key}"
    matchup_key_reverse = f"{team2_key}_{team1_key}"
    
    # Check for game ID clues in case of same-city teams - using generic check
    same_city_teams = False
    if team1_code and team2_code and team1_code != team2_code:
        print(f"Different team codes detected: {team1_code} vs {team2_code} - treating as different teams")
        same_city_teams = True
    
    # Only skip if this exact matchup has already been processed
    # Skip duplicate detection if we've identified this as a same-city matchup
    if not same_city_teams and (matchup_key in processed_game_ids or matchup_key_reverse in processed_game_ids):
        print(f"Skipping duplicate game: {team1_official} vs {team2_official} - already processed")
        print(f"--- SKIPPED PROCESSING: Duplicate matchup already processed ---\n")
        return game_times
    
    # Initialize result data
    game_result = None
    winner = None
    loser = None
    
    # Look for game results for completed games (by checking RESULT column)
    game_status = "upcoming"  # Default status
    
    # Special handling for postponed games - treat them as completed
    if is_postponed:
        game_status = "completed"
        game_result = "Postponed"
        print(f"Setting game status to COMPLETED (POSTPONED): {team1_official} vs {team2_official}")
    
    # Check for result cells if not already marked as postponed
    if not is_postponed:
        result_cells = row.find_all('td', class_='Table__TD', attrs={'data-header': 'RESULT'})
        if not result_cells:
            # Try direct column name matching as well
            result_cells = row.find_all('td', string=lambda x: x and 'RESULT' in x)
            
            # Check for cells with "RESULT" in header
            if not result_cells:
                for cell in team_cells:
                    if cell.get('data-header') == 'RESULT':
                        result_cells = [cell]
                        break
            
        if result_cells:
            result_cell = result_cells[0]
            result_text = result_cell.text.strip()
            print(f"Found result cell with text: '{result_text}'")
            
            # Check for common result formats including postponed
            if result_text.upper() in ["POSTPONED", "PPD"]:
                game_status = "completed"
                game_result = "Postponed"
                print(f"Found POSTPONED game from result cell: {team1_official} vs {team2_official}")
            else:
                game_status = "completed"
                game_result = result_text
            
            if is_mlb:
                print(f"  MLB GAME COMPLETED: Found result cell for {team1_official} vs {team2_official}")
                print(f"  Result: {result_text}")
                
                # For MLB, also try to parse the score from the result text if not postponed
                if result_text.upper() not in ["POSTPONED", "PPD"]:
                    score_match = re.search(r'(\d+)[\s,]*[-]?[\s,]*(\d+)', result_text)
                    if score_match:
                        score1, score2 = score_match.group(1), score_match.group(2)
                        game_result = f"{score1}-{score2}"
                        print(f"  Parsed MLB score from result text: {game_result}")
        
    # Get game time - look for time in different possible cells
    time_cell = None
    time_text = None
    
    print(f"\n--- PROCESSING GAME: {team1} vs {team2} ---")
    
    # Look for game time in different cells - varies by sport
    for cell in team_cells:
        cell_text = cell.text.strip()
        cell_class = cell.get('class', [])
        
        # Check for date_col class which often contains time
        if 'date__col' in cell_class or ':' in cell_text or 'LIVE' in cell_text or 'PM' in cell_text or 'AM' in cell_text:
            time_cell = cell
            time_text = cell_text
            print(f"Found time cell with text: '{time_text}' (class: {cell_class})")
            break
    
    # If no time cell was found, look for gameStatus cells specifically
    if not time_text:
        game_status_cells = row.find_all('td', class_=lambda x: x and ('gameStatus' in x.lower() or 'game-status' in x.lower()))
        if game_status_cells:
            time_text = game_status_cells[0].text.strip()
    
    # If still no time, check if there's a cell with just time pattern
    if not time_text:
        for cell in team_cells:
            cell_text = cell.text.strip()
            # Look for typical time formats (e.g., 8:00 PM)
            if re.search(r'\d{1,2}:\d{2}\s*(?:AM|PM|ET|EST|EDT)?', cell_text):
                time_text = cell_text
                break
            # Also check for any in-progress or live status indicators
            elif any(status in cell_text.upper() for status in ['LIVE', 'IN PROGRESS', 'ONGOING']):
                time_text = 'LIVE'
                break
    
    # If we still don't have a time, check for game status in the entire row
    if not time_text:
        row_text = row.text.strip().upper()
        print(f"Checking row text for live indicators: '{row_text}'")
        if any(status in row_text for status in ['LIVE', 'IN PROGRESS', 'ONGOING']):
            time_text = 'LIVE'
            print(f"Found LIVE status in row text")
        else:
            print(f"Skipping {team1} vs {team2} - no time found")
            print(f"--- SKIPPED PROCESSING: No time information ---\n")
            return game_times
    
    # Skip games with TBD status, but keep Postponed games
    if time_text and any(status in time_text for status in ['TBD']):
        print(f"Skipping {team1} vs {team2} - time is {time_text}")
        print(f"--- SKIPPED PROCESSING: Game status is {time_text} ---\n")
        return game_times
    
    # Don't skip Postponed games - they should be treated as completed with a special result
    if time_text and any(status in time_text for status in ['Postponed', 'PPD']):
        game_status = "completed"
        game_result = "Postponed"
        print(f"Found POSTPONED game from time text: {team1_official} vs {team2_official}")
    
    # Check if game is final, in progress, or scheduled
    if "LIVE" in time_text.upper() or "IN PROGRESS" in time_text.upper():
        game_status = "live"
        print(f"Setting game status to LIVE: {team1} vs {team2}")
        
        # Also ensure any content with the word "LIVE" is captured
        for cell in team_cells:
            cell_content = cell.text.strip().upper()
            if "LIVE" in cell_content:
                print(f"Found additional LIVE indicator in cell text: {cell_content}")
    elif "FINAL" in time_text.upper() or "F/" in time_text.upper():
        # Process games that are already finished
        game_status = "completed"
        print(f"Setting game status to COMPLETED: {team1} vs {team2}")
        
        # Extract result if available
        result_text = "Final"
        # Look for a score in the time text (common format: "F 5-3")
        score_match = re.search(r'F\s+(\d+)[^\d]+(\d+)', time_text)
        if score_match:
            result_text = f"{score_match.group(1)}-{score_match.group(2)}"
            print(f"Extracted score from time: {result_text}")
        
        # If we don't have a score yet, check all cells for score patterns
        if result_text == "Final":
            for cell in team_cells:
                cell_text = cell.text.strip()
                # Look for common score patterns like "5-3", "W 5-3", etc.
                score_match = re.search(r'(?:^|\s)(\d+)[-\s]+(\d+)(?:\s|$)', cell_text)
                if score_match:
                    result_text = f"{score_match.group(1)}-{score_match.group(2)}"
                    print(f"Found score in cell: {result_text} from '{cell_text}'")
                    break
        
        # If we already have a game_result from result column, use that instead
        if game_result:
            result_text = game_result
            print(f"Using result from column: {result_text}")
        else:
            game_result = result_text
        
        # Look for WIN/LOSS information if we don't have it already
        if not winner or not loser:
            # Try to find specific win/loss cells or pitcher information
            for cell in team_cells:
                cell_text = cell.text.strip()
                # Look for WIN: Player patterns
                win_match = re.search(r'(?:WIN|W):\s*([^,;]+)', cell_text, re.IGNORECASE)
                if win_match and not winner:
                    winner = win_match.group(1).strip()
                    print(f"Extracted winner: {winner}")
                
                # Look for LOSS: Player patterns
                loss_match = re.search(r'(?:LOSS|L):\s*([^,;]+)', cell_text, re.IGNORECASE)
                if loss_match and not loser:
                    loser = loss_match.group(1).strip()
                    print(f"Extracted loser: {loser}")
    
    # Also check status columns for FINAL indicators if game is not already marked as completed
    if game_status != "completed" and game_status != "live":
        for cell in team_cells:
            cell_content = cell.text.strip().upper()
            # Look for FINAL, F, F/OT (Final in Overtime)
            if re.search(r'\b(FINAL|F(/\w+)?)\b', cell_content):
                print(f"Found FINAL indicator in cell: {cell_content}")
                game_status = "completed"
                game_result = "Final"
                
                if is_mlb:
                    print(f"  MLB GAME COMPLETED: Found FINAL indicator for {team1_official} vs {team2_official}")
                
                # Try to extract score from this cell or surrounding cells
                score_match = re.search(r'(\d+)[-\s]+(\d+)', cell_content)
                if score_match:
                    game_result = f"{score_match.group(1)}-{score_match.group(2)}"
                    print(f"Extracted score from final cell: {game_result}")
                break
    
    # Add special MLB-specific checks for completed games
    if is_mlb and game_status != "completed":
        # Look for any indications this is a completed MLB game
        for cell in team_cells:
            cell_content = str(cell).upper()
            cell_text = cell.text.strip().upper()
            
            # Check for specific MLB completion indicators
            if any(indicator in cell_text for indicator in ['FINAL', 'F/', 'GAME OVER', 'COMPLETE']) or \
               any(indicator in cell_content for indicator in ['FINAL', 'F/', 'GAME OVER', 'COMPLETE']):
                print(f"  MLB SPECIFIC: Found completion indicator in cell: {cell_text}")
                game_status = "completed"
                game_result = "Final"
                break
    
    # Special handling for MLB FINAL games - force them to be completed if not already
    if is_mlb:
        row_text = row.text.strip().upper()
        if "FINAL" in row_text and game_status != "completed":
            game_status = "completed"
            print(f"  Forcing MLB game to COMPLETED status due to FINAL indicator")
            
            # Look for a score pattern in the row text (common for MLB)
            score_pattern = re.search(r'(\d+)\s*[-]\s*(\d+)', row_text)
            if score_pattern:
                score1, score2 = score_pattern.group(1), score_pattern.group(2)
                game_result = f"{score1}-{score2}"
                print(f"  Extracted MLB score from row: {game_result}")
                
        # Additional check for the "FINAL" indicator in any cell
        for cell in team_cells:
            if "FINAL" in cell.text.strip().upper():
                game_status = "completed"
                print(f"  Found MLB FINAL indicator in a cell")
    
    # Also check for RESULT column with postponed games
    if game_status != "completed":
        for cell in team_cells:
            if cell.get('data-header') == 'RESULT':
                cell_content = cell.text.strip().upper()
                if "POSTPONED" in cell_content or "PPD" in cell_content:
                    game_status = "completed"
                    game_result = "Postponed"
                    print(f"Found POSTPONED in RESULT column: {cell_content}")
                    break
    
    # Process based on game status
    if game_status == "live":
        # Game is live, add to game_times
        return process_live_game(
            sport, team1, team2, team1_official, team2_official,
            game_id, row_position, table_idx, section_date,
            team1_key, team2_key, teams_with_games_today, processed_game_ids,
            game_times
        )
    elif game_status == "completed":
        # Game is completed, add to game_times
        if is_mlb:
            print(f"  SENDING MLB GAME TO COMPLETED PROCESSOR: {team1_official} vs {team2_official}")
            print(f"  Result: {game_result}")
            
        return process_completed_game(
            sport, team1, team2, team1_official, team2_official,
            game_id, row_position, table_idx, section_date,
            team1_key, team2_key, teams_with_games_today, processed_game_ids,
            game_result, winner, loser,
            game_times
        )
    elif time_text and ":" in time_text and ("ET" in time_text or "PM" in time_text or "AM" in time_text):
        # Regular time format, add to game_times
        return process_upcoming_game(
            sport, team1, team2, team1_official, team2_official,
            game_id, row_position, table_idx, section_date,
            team1_key, team2_key, teams_with_games_today, processed_game_ids,
            time_text, game_times
        )
    else:
        print(f"Skipping {team1} vs {team2} - time format not recognized: {time_text}")
        print(f"--- SKIPPED PROCESSING: Unrecognized time format ---\n")
        return game_times 