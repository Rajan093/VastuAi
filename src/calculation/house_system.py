"""
Lal Kitab specific house system and rules.
"""

from typing import Dict, List


class LalKitabHouseSystem:
    """Lal Kitab house system utilities."""
    
    @staticmethod
    def validate_chart(chart: Dict[str, int]) -> bool:
        """
        Validate if a chart has all required planets.
        
        Args:
            chart: Planet-house mapping
            
        Returns:
            True if valid, False otherwise
        """
        required_planets = [
            'Sun', 'Moon', 'Mars', 'Mercury', 
            'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'
        ]
        
        for planet in required_planets:
            if planet not in chart:
                return False
            
            house = chart[planet]
            if not (1 <= house <= 12):
                return False
        
        return True
    
    @staticmethod
    def get_planets_in_house(chart: Dict[str, int], house: int) -> List[str]:
        """
        Get all planets positioned in a specific house.
        
        Args:
            chart: Planet-house mapping
            house: House number (1-12)
            
        Returns:
            List of planet names in that house
        """
        return [planet for planet, h in chart.items() if h == house]
    
    @staticmethod
    def format_chart_by_houses(chart: Dict[str, int]) -> str:
        """
        Format chart grouped by houses.
        
        Args:
            chart: Planet-house mapping
            
        Returns:
            Formatted string showing planets in each house
        """
        output = "Chart by Houses:\n"
        output += "=" * 50 + "\n"
        
        for house in range(1, 13):
            planets = LalKitabHouseSystem.get_planets_in_house(chart, house)
            planets_str = ", ".join(planets) if planets else "Empty"
            output += f"House {house:2d}: {planets_str}\n"
        
        return output

