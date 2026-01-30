from typing import List, Dict, Optional
from .regex_parser import RegexParser


class LalKitabChunker:
    
    def __init__(self):
        self.parser = RegexParser()
    
    def extract_chunks(self, text: str) -> List[Dict[str, any]]:
        """
        Extract all planet-house chunks from the text.
        
        Args:
            text: The full text content
            
        Returns:
            List of dictionaries containing:
                - planet: Planet name
                - house: House number (1-12)
                - content: The full text block for this combination
                - heading: The original heading text
        """
        # Find all planet-house headings
        headings = self.parser.find_all_planet_house_headings(text)
        
        if not headings:
            return []
        
        chunks = []
        
        for i, heading in enumerate(headings):
            # Determine where this chunk ends
            # It ends at the start of the next heading, or at the end of the text
            start_pos = heading['start_pos']
            
            if i < len(headings) - 1:
                end_pos = headings[i + 1]['start_pos']
            else:
                end_pos = len(text)
            
            chunk_text = text[start_pos:end_pos].strip()
            
            chunk = {
                'planet': heading['planet'],
                'house': heading['house'],
                'heading': heading['match_text'],
                'content': chunk_text,
                'char_count': len(chunk_text)
            }
            
            chunks.append(chunk)
        
        return chunks
    
    def get_chunk_summary(self, chunks: List[Dict[str, any]]) -> Dict[str, any]:
        if not chunks:
            return {
                'total_chunks': 0,
                'total_chars': 0,
                'avg_chars_per_chunk': 0,
                'planets_covered': [],
                'houses_covered': []
            }
        
        total_chars = sum(chunk['char_count'] for chunk in chunks)
        planets = sorted(set(chunk['planet'] for chunk in chunks))
        houses = sorted(set(chunk['house'] for chunk in chunks))
        
        return {
            'total_chunks': len(chunks),
            'total_chars': total_chars,
            'avg_chars_per_chunk': total_chars // len(chunks),
            'planets_covered': planets,
            'houses_covered': houses
        }


if __name__ == "__main__":
    # Test the chunker
    chunker = LalKitabChunker()
    
    test_text = """
Sun in 1st House
Benefic: The native will be good and wealthy.
Malefic: Health problems may occur.

Sun in 2nd house
Benefic: Good family life.
Malefic: Disputes in family.

Moon in 3rd House
Benefic: Intelligent and wise.
Malefic: Mental stress possible.
"""
    
    chunks = chunker.extract_chunks(test_text)
    summary = chunker.get_chunk_summary(chunks)
    
    print(f"Extracted {summary['total_chunks']} chunks")
    print(f"Planets: {summary['planets_covered']}")
    print(f"Houses: {summary['houses_covered']}")
    print("\nFirst chunk:")
    if chunks:
        print(f"Planet: {chunks[0]['planet']}")
        print(f"House: {chunks[0]['house']}")
        print(f"Content preview: {chunks[0]['content'][:100]}...")
