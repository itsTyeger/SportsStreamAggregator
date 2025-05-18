import requests
from bs4 import BeautifulSoup
import re

def examine_espn_page():
    """Examine the ESPN MLB schedule page to find date headers and their structure."""
    url = "https://www.espn.com/mlb/schedule"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Successfully retrieved page, status code: {response.status_code}")
        
        # Save the HTML to a file for reference
        with open("espn_schedule.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved HTML to espn_schedule.html")
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different approaches to find date headers
        print("\n===== Approach 1: Looking for Table__Title class =====")
        date_headers = soup.find_all('h2', class_='Table__Title')
        print(f"Found {len(date_headers)} headers with class 'Table__Title'")
        for i, header in enumerate(date_headers):
            print(f"Header {i+1}: {header.text.strip()}")
            
        print("\n===== Approach 2: Looking for day names in headings =====")
        day_patterns = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        day_headers = []
        
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']):
            text = tag.text.strip()
            if any(day in text for day in day_patterns) and re.search(r'\d{4}', text):  # Contains day name and year
                day_headers.append((tag.name, text, tag.get('class')))
                
        print(f"Found {len(day_headers)} headers containing day names and years")
        for i, (tag_name, text, classes) in enumerate(day_headers):
            class_str = ', '.join(classes) if classes else 'None'
            print(f"Day header {i+1}: <{tag_name}> with classes [{class_str}] - Text: '{text}'")
            
        print("\n===== Approach 3: Looking for specific date format =====")
        date_pattern = re.compile(r'(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday),\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}')
        
        for tag in soup.find_all(string=date_pattern):
            parent = tag.parent
            print(f"Found date '{tag.strip()}' in <{parent.name}> with classes: {parent.get('class')}")
            # Print the parent chain to understand structure
            parent_chain = []
            current = parent
            while current and current.name != 'body':
                classes = current.get('class')
                class_str = f" class='{' '.join(classes)}'" if classes else ""
                parent_chain.append(f"<{current.name}{class_str}>")
                current = current.parent
            print("Parent chain:", " > ".join(reversed(parent_chain)))
            
        print("\n===== Approach 4: Examining page sections =====")
        sections = soup.find_all(['section', 'div'], class_=lambda c: c and ('ScheduleTables' in c or 'Wrapper' in c or 'Table' in c))
        print(f"Found {len(sections)} potential schedule sections")
        
        for i, section in enumerate(sections):
            # Try to find a date heading within this section
            date_text = None
            
            # Look for dates in headings
            headings = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                if date_pattern.search(heading.text):
                    date_text = heading.text.strip()
                    break
            
            # If no date in headings, look through all text
            if not date_text:
                section_texts = section.find_all(string=date_pattern)
                if section_texts:
                    date_text = section_texts[0].strip()
            
            # Report section and any date found
            classes = section.get('class')
            class_str = f"class='{' '.join(classes)}'" if classes else "no class"
            if date_text:
                print(f"Section {i+1}: <{section.name} {class_str}> contains date: '{date_text}'")
            else:
                print(f"Section {i+1}: <{section.name} {class_str}> - No date found")
        
    except Exception as e:
        print(f"Error examining ESPN page: {str(e)}")

if __name__ == "__main__":
    examine_espn_page() 