"""
Horoscope calculator using Swiss Ephemeris (pyswisseph).
Calculates planetary positions from birth data.
"""

import swisseph as swe
from datetime import datetime
from typing import Dict, Tuple


class HoroscopeCalculator:
    """Calculate planetary positions using Swiss Ephemeris."""
    
    # Planet IDs in Swiss Ephemeris
    PLANETS = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mars': swe.MARS,
        'Mercury': swe.MERCURY,
        'Jupiter': swe.JUPITER,
        'Venus': swe.VENUS,
        'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE,  # North Node (Rahu)
        'Ketu': swe.MEAN_NODE   # South Node (Ketu) - 180° opposite to Rahu
    }
    
    def __init__(self):
        """Initialize the calculator."""
        # Swiss Ephemeris uses sidereal zodiac for Vedic astrology
        swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri ayanamsa (most common in Vedic)
    
    def calculate_julian_day(
        self, 
        year: int, 
        month: int, 
        day: int, 
        hour: int, 
        minute: int,
        timezone_offset: float = 0.0
    ) -> float:
        """
        Calculate Julian Day Number for the given date and time.
        
        Args:
            year: Birth year
            month: Birth month (1-12)
            day: Birth day
            hour: Birth hour (0-23)
            minute: Birth minute (0-59)
            timezone_offset: Timezone offset from UTC (e.g., +5.5 for IST)
            
        Returns:
            Julian Day Number
        """
        # Convert to UTC
        utc_hour = hour - timezone_offset
        
        # Calculate Julian Day
        jd = swe.julday(year, month, day, utc_hour + minute / 60.0)
        return jd
    
    def calculate_ascendant(
        self, 
        jd: float, 
        latitude: float, 
        longitude: float
    ) -> float:
        """
        Calculate the Ascendant (Lagna) degree.
        
        Args:
            jd: Julian Day Number
            latitude: Birth place latitude
            longitude: Birth place longitude
            
        Returns:
            Ascendant degree in the zodiac (0-360)
        """
        # Calculate houses using Placidus system
        cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
        
        # Return Ascendant (first element in ascmc array)
        return ascmc[0]
    
    def calculate_planet_position(
        self, 
        planet_id: int, 
        jd: float
    ) -> float:
        """
        Calculate a planet's position in degrees.
        
        Args:
            planet_id: Swiss Ephemeris planet ID
            jd: Julian Day Number
            
        Returns:
            Planet's longitude in degrees (0-360)
        """
        # Calculate planet position (sidereal)
        result = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        
        # Return longitude (first element)
        return result[0][0]
    
    def degree_to_house(
        self, 
        planet_degree: float, 
        ascendant_degree: float
    ) -> int:
        """
        Calculate which house a planet is in (Lal Kitab system).
        In Lal Kitab, Ascendant is always the 1st house.
        
        Args:
            planet_degree: Planet's degree in zodiac (0-360)
            ascendant_degree: Ascendant degree (0-360)
            
        Returns:
            House number (1-12)
        """
        # Calculate distance from ascendant
        distance = (planet_degree - ascendant_degree) % 360
        
        # Each house is 30 degrees
        house = int(distance / 30) + 1
        
        return house
    
    def calculate_chart(
        self,
        date: str,  # Format: "YYYY-MM-DD"
        time: str,  # Format: "HH:MM"
        latitude: float,
        longitude: float,
        timezone_offset: float = 5.5  # Default: IST (+5:30)
    ) -> Dict[str, int]:
        """
        Calculate complete horoscope chart.
        
        Args:
            date: Birth date (YYYY-MM-DD)
            time: Birth time (HH:MM)
            latitude: Birth place latitude
            longitude: Birth place longitude
            timezone_offset: Timezone offset from UTC
            
        Returns:
            Dictionary mapping planet names to house numbers
            Example: {"Sun": 10, "Moon": 4, "Mars": 7, ...}
        """
        # Parse date and time
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Calculate Julian Day
        jd = self.calculate_julian_day(
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute,
            timezone_offset
        )
        
        # Calculate Ascendant
        ascendant = self.calculate_ascendant(jd, latitude, longitude)
        
        # Calculate planetary positions
        chart = {}
        
        for planet_name, planet_id in self.PLANETS.items():
            if planet_name == 'Ketu':
                # Ketu is 180° opposite to Rahu
                rahu_degree = self.calculate_planet_position(planet_id, jd)
                ketu_degree = (rahu_degree + 180) % 360
                house = self.degree_to_house(ketu_degree, ascendant)
            else:
                planet_degree = self.calculate_planet_position(planet_id, jd)
                house = self.degree_to_house(planet_degree, ascendant)
            
            chart[planet_name] = house
        
        return chart
    
    def calculate_chart_by_place(
        self,
        date: str,  # Format: "YYYY-MM-DD"
        time: str,  # Format: "HH:MM"
        place_name: str,  # e.g., "Ahmedabad" or "Mumbai, Maharashtra"
        timezone_offset: float = 5.5  # Default: IST (+5:30)
    ) -> Dict[str, int]:
        """
        Calculate horoscope chart using place name (auto-geocoding).
        
        Args:
            date: Birth date (YYYY-MM-DD)
            time: Birth time (HH:MM)
            place_name: Birth place name (will be geocoded to coordinates)
            timezone_offset: Timezone offset from UTC
            
        Returns:
            Dictionary mapping planet names to house numbers
            
        Raises:
            RuntimeError: If place name cannot be geocoded
        """
        from .geocoding import get_coordinates
        
        # Get coordinates from place name
        coords = get_coordinates(place_name)
        
        if not coords:
            raise RuntimeError(
                f"Could not find coordinates for '{place_name}'. "
                "Please check the spelling or provide coordinates manually."
            )
        
        latitude, longitude = coords
        
        # Calculate chart using coordinates
        return self.calculate_chart(
            date=date,
            time=time,
            latitude=latitude,
            longitude=longitude,
            timezone_offset=timezone_offset
        )
    
    def get_chart_summary(self, chart: Dict[str, int]) -> str:
        """
        Get a formatted summary of the chart.
        
        Args:
            chart: Dictionary of planet-house mappings
            
        Returns:
            Formatted string representation
        """
        summary = "Horoscope Chart:\n"
        summary += "=" * 40 + "\n"
        
        for planet, house in sorted(chart.items()):
            summary += f"{planet:8s} → House {house:2d}\n"
        
        return summary
