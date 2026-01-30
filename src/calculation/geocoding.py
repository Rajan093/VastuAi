"""
Geocoding utilities to convert place names to coordinates.
Uses Nominatim (OpenStreetMap) - free and no API key required.
"""

import ssl
import certifi
from typing import Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


class Geocoder:
    """Convert place names to latitude/longitude coordinates."""
    
    def __init__(self, user_agent: str = "astrochat-lal-kitab"):
        """
        Initialize the geocoder.
        
        Args:
            user_agent: Identifier for the geocoding service
        """
        # Create SSL context that doesn't verify certificates (for local development)
        ctx = ssl.create_default_context(cafile=certifi.where())
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # Initialize Nominatim geocoder (free, based on OpenStreetMap)
        self.geolocator = Nominatim(
            user_agent=user_agent, 
            timeout=10,
            ssl_context=ctx
        )
    
    def get_coordinates(
        self, 
        place_name: str,
        country: str = "India"
    ) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude for a place name.
        
        Args:
            place_name: Name of the place (e.g., "Ahmedabad", "Mumbai, Maharashtra")
            country: Country name to improve accuracy (default: "India")
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
            
        Example:
            >>> geocoder = Geocoder()
            >>> coords = geocoder.get_coordinates("Ahmedabad")
            >>> print(coords)
            (23.0225, 72.5714)
        """
        try:
            # Add country to query for better accuracy
            full_query = f"{place_name}, {country}"
            
            # Query Nominatim
            location = self.geolocator.geocode(full_query)
            
            if location:
                return (location.latitude, location.longitude)
            else:
                # Try without country if first attempt fails
                location = self.geolocator.geocode(place_name)
                if location:
                    return (location.latitude, location.longitude)
                return None
                
        except GeocoderTimedOut:
            raise RuntimeError(
                f"Geocoding request timed out for '{place_name}'. "
                "Please check your internet connection and try again."
            )
        except GeocoderServiceError as e:
            raise RuntimeError(
                f"Geocoding service error: {str(e)}"
            )
        except Exception as e:
            raise RuntimeError(
                f"Error geocoding '{place_name}': {str(e)}"
            )
    
    def get_coordinates_with_details(
        self, 
        place_name: str,
        country: str = "India"
    ) -> Optional[dict]:
        """
        Get detailed location information including coordinates.
        
        Args:
            place_name: Name of the place
            country: Country name (default: "India")
            
        Returns:
            Dictionary with location details or None if not found
            
        Example:
            >>> geocoder = Geocoder()
            >>> details = geocoder.get_coordinates_with_details("Ahmedabad")
            >>> print(details)
            {
                'place_name': 'Ahmedabad, Gujarat, India',
                'latitude': 23.0225,
                'longitude': 72.5714,
                'address': {...}
            }
        """
        try:
            full_query = f"{place_name}, {country}"
            location = self.geolocator.geocode(full_query, addressdetails=True)
            
            if not location:
                location = self.geolocator.geocode(place_name, addressdetails=True)
            
            if location:
                return {
                    'place_name': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'raw_address': location.raw.get('address', {})
                }
            return None
            
        except Exception as e:
            raise RuntimeError(
                f"Error getting location details for '{place_name}': {str(e)}"
            )


# Convenience function for quick geocoding
def get_coordinates(place_name: str, country: str = "India") -> Optional[Tuple[float, float]]:
    """
    Quick geocoding function.
    
    Args:
        place_name: Name of the place
        country: Country name (default: "India")
        
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    geocoder = Geocoder()
    return geocoder.get_coordinates(place_name, country)

