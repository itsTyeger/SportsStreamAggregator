import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz

def analyze_espn_dates():
    """Analyze the date structure in ESPN schedules for different sports."""
    sports = {
        'MLB': 'https://www.espn.com/mlb/schedule',
        'NBA': 'https://www.espn.com/nba/schedule',
        'NHL': 'https://www.espn.com/nhl/schedule',
        'NFL': 'https://www.espn.com/nfl/schedule'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for sport, url in sports.items():
        print(f"\n{'='*80}")
        print(f"Analyzing {sport} schedule at {url}")
        print(f"{'='*80}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Save the HTML to a file for reference
            with open(f"espn_{sport}_schedule.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Saved HTML to espn_{sport}_schedule.html")
            
            # Approach 1: Look for Table__Title class
            print("\nApproach 1: Searching for Table__Title class")
            date_headers = soup.find_all('h2', class_='Table__Title')
            print(f"Found {len(date_headers)} date headers with Table__Title class")
            for i, header in enumerate(date_headers):
                print(f"  Header {i+1}: {header.text.strip()}")
            
            # Approach 2: Look for text with date format patterns
            print("\nApproach 2: Searching for day name + month + day + year pattern")
            day_patterns = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            month_patterns = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
                              'August', 'September', 'October', 'November', 'December']
            
            date_elements = []
            
            # Look for common date formats in text
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span', 'a']):
                text = element.get_text().strip()
                
                # Pattern like "Sunday, May 19, 2024"
                if any(day in text for day in day_patterns) and any(month in text for month in month_patterns) and re.search(r'\d{4}', text):
                    date_elements.append((element.name, text, element.get('class')))
            
            print(f"Found {len(date_elements)} elements with date-like text")
            for i, (tag_name, text, classes) in enumerate(date_elements):
                class_str = ', '.join(classes) if classes else 'None'
                print(f"  Element {i+1}: <{tag_name}> with classes [{class_str}]: {text}")
                
                # Try to extract parent structure for potential table associations
                parent = element.parent
                if parent:
                    parent_class = parent.get('class')
                    print(f"    Parent: <{parent.name}> with classes [{', '.join(parent_class) if parent_class else 'None'}]")
                    
                    # Look for nearby tables
                    next_sibling = parent.find_next_sibling()
                    if next_sibling:
                        sibling_class = next_sibling.get('class')
                        print(f"    Next sibling: <{next_sibling.name}> with classes [{', '.join(sibling_class) if sibling_class else 'None'}]")
            
            # Approach 3: Look for div elements with date IDs or classes
            print("\nApproach 3: Searching for elements with date-related attributes")
            date_attr_elements = soup.find_all(lambda tag: tag.has_attr('data-date') or 
                                            (tag.has_attr('id') and ('date' in tag['id'].lower() or 'day' in tag['id'].lower())) or
                                            (tag.has_attr('class') and any('date' in c.lower() or 'day' in c.lower() for c in tag['class'])))
            
            print(f"Found {len(date_attr_elements)} elements with date-related attributes")
            for i, element in enumerate(date_attr_elements):
                attr_info = []
                if element.has_attr('data-date'):
                    attr_info.append(f"data-date={element['data-date']}")
                if element.has_attr('id'):
                    attr_info.append(f"id={element['id']}")
                if element.has_attr('class'):
                    attr_info.append(f"class={' '.join(element['class'])}")
                
                text = element.get_text().strip()
                if len(text) > 100:
                    text = text[:100] + "..."
                    
                print(f"  Element {i+1}: <{element.name}> {', '.join(attr_info)}")
                print(f"    Text: {text}")
            
            # Approach 4: Find all responsive tables and look at their content
            print("\nApproach 4: Examining all ResponsiveTable elements")
            tables = soup.find_all('div', class_='ResponsiveTable')
            print(f"Found {len(tables)} tables with ResponsiveTable class")
            
            for i, table in enumerate(tables):
                # Look for heading before this table
                header = None
                for prev_element in table.previous_elements:
                    if prev_element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        header = prev_element.get_text().strip()
                        break
                
                # Get first row as sample
                game_rows = table.find_all('tr', class_=lambda x: x and 'Table__TR' in x)
                game_rows = [row for row in game_rows if not row.find('th')]  # Skip header rows
                
                print(f"  Table {i+1}: Found {len(game_rows)} game rows")
                print(f"    Preceding header: {header or 'None'}")
                
                if game_rows:
                    # Sample the first game
                    sample_row = game_rows[0]
                    team_cells = sample_row.find_all('td', class_='Table__TD')
                    
                    # Try to extract teams
                    team_links = sample_row.find_all('a', class_='AnchorLink')
                    team_links = [link for link in team_links if link.find('abbr') or '/team/' in link.get('href', '') or 'gamecast' not in link.get('href', '')]
                    
                    team1 = team_links[0].text.strip() if len(team_links) >= 1 else "Unknown"
                    team2 = team_links[1].text.strip() if len(team_links) >= 2 else "Unknown"
                    
                    # Try to extract game time
                    time_text = None
                    for cell in team_cells:
                        cell_text = cell.text.strip()
                        if ':' in cell_text or 'LIVE' in cell_text or 'PM' in cell_text or 'AM' in cell_text:
                            time_text = cell_text
                            break
                    
                    print(f"    Sample game: {team1} vs {team2} - Time: {time_text or 'Unknown'}")
            
        except Exception as e:
            print(f"Error analyzing {sport} schedule: {str(e)}")

if __name__ == "__main__":
    analyze_espn_dates() 