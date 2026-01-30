import re
from typing import Dict, List


class RegexParser:
    
    PLANETS = [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", 
        "Venus", "Saturn", "Rahu", "Ketu"
    ]
    
    def __init__(self):
        self.planet_house_pattern = re.compile(
            r'^(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)\s+in\s+(\d+|I)(?:st|nd|rd|th)?\s+[Hh]ouse',
            re.MULTILINE | re.IGNORECASE
        )
    
    def find_all_planet_house_headings(self, text: str) -> List[Dict[str, any]]:
        matches = []
        for match in self.planet_house_pattern.finditer(text):
            planet = match.group(1).capitalize()
            house_str = match.group(2)
            house = 1 if house_str.upper() == 'I' else int(house_str)
            
            matches.append({
                'planet': planet,
                'house': house,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'match_text': match.group(0)
            })
        
        return matches

if __name__ == "__main__":
    # Test the regex parser
    parser = RegexParser()
    
    # Sample test text
    test_text = """
    Sun in 1st House
    This is some content about Sun in first house.
    
    Sun in 2nd house
    This is content about Sun in second house.
    
    Moon in 3rd House
    Content about Moon.
    """
    
    matches = parser.find_all_planet_house_headings(test_text)
    print(f"Found {len(matches)} matches:")
    for match in matches:
        print(f"  - {match['planet']} in House {match['house']} at position {match['start_pos']}")
