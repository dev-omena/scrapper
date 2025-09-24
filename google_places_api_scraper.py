"""
Google Places API Alternative Scraper
This provides a more reliable alternative to Chrome scraping for Railway deployment
"""

import requests
import json
import time
from typing import List, Dict, Optional

class GooglePlacesAPIScraper:
    def __init__(self, api_key: str):
        """
        Initialize with Google Places API key
        Get your API key from: https://console.cloud.google.com/apis/credentials
        """
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
    def search_places(self, query: str, location: str = "Cairo, Egypt", radius: int = 5000) -> List[Dict]:
        """
        Search for places using Google Places API
        
        Args:
            query: Search query (e.g., "كافيهات في كليه البنات")
            location: Location to search around
            radius: Search radius in meters
            
        Returns:
            List of place dictionaries with details
        """
        
        # First, get coordinates for the location
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {
            'address': location,
            'key': self.api_key
        }
        
        try:
            geocode_response = requests.get(geocode_url, params=geocode_params)
            geocode_data = geocode_response.json()
            
            if geocode_data['status'] != 'OK':
                print(f"Geocoding failed: {geocode_data['status']}")
                return []
                
            lat = geocode_data['results'][0]['geometry']['location']['lat']
            lng = geocode_data['results'][0]['geometry']['location']['lng']
            
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return []
        
        # Search for places
        search_url = f"{self.base_url}/textsearch/json"
        search_params = {
            'query': query,
            'location': f"{lat},{lng}",
            'radius': radius,
            'key': self.api_key
        }
        
        all_results = []
        next_page_token = None
        
        while True:
            if next_page_token:
                search_params['pagetoken'] = next_page_token
                time.sleep(2)  # Required delay for next page
            
            try:
                response = requests.get(search_url, params=search_params)
                data = response.json()
                
                if data['status'] not in ['OK', 'ZERO_RESULTS']:
                    print(f"API Error: {data['status']}")
                    break
                
                if 'results' in data:
                    for place in data['results']:
                        place_details = self.get_place_details(place['place_id'])
                        if place_details:
                            all_results.append(place_details)
                
                # Check for next page
                next_page_token = data.get('next_page_token')
                if not next_page_token:
                    break
                    
            except Exception as e:
                print(f"Error searching places: {e}")
                break
        
        return all_results
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information for a specific place"""
        
        details_url = f"{self.base_url}/details/json"
        details_params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,opening_hours,price_level,photos,geometry,types',
            'key': self.api_key
        }
        
        try:
            response = requests.get(details_url, params=details_params)
            data = response.json()
            
            if data['status'] != 'OK':
                return None
                
            result = data['result']
            
            # Format the data similar to scraped data
            place_data = {
                'name': result.get('name', ''),
                'address': result.get('formatted_address', ''),
                'phone': result.get('formatted_phone_number', ''),
                'website': result.get('website', ''),
                'rating': result.get('rating', 0),
                'reviews_count': result.get('user_ratings_total', 0),
                'price_level': result.get('price_level', 0),
                'types': result.get('types', []),
                'latitude': result.get('geometry', {}).get('location', {}).get('lat', 0),
                'longitude': result.get('geometry', {}).get('location', {}).get('lng', 0),
                'opening_hours': result.get('opening_hours', {}).get('weekday_text', []),
                'place_id': place_id
            }
            
            return place_data
            
        except Exception as e:
            print(f"Error getting place details: {e}")
            return None

# Example usage function
def scrape_with_api(query: str, api_key: str) -> List[Dict]:
    """
    Main function to scrape using Google Places API
    
    Args:
        query: Search query (e.g., "كافيهات في كليه البنات")
        api_key: Google Places API key
        
    Returns:
        List of place data dictionaries
    """
    
    scraper = GooglePlacesAPIScraper(api_key)
    
    # Extract location from query if possible
    if "في" in query:  # Arabic "in"
        parts = query.split("في")
        if len(parts) > 1:
            location = parts[1].strip() + ", Cairo, Egypt"
        else:
            location = "Cairo, Egypt"
    else:
        location = "Cairo, Egypt"
    
    print(f"Searching for: {query}")
    print(f"Location: {location}")
    
    results = scraper.search_places(query, location)
    
    print(f"Found {len(results)} places")
    
    return results

if __name__ == "__main__":
    # Example usage
    API_KEY = "YOUR_GOOGLE_PLACES_API_KEY_HERE"
    query = "كافيهات في كليه البنات"
    
    results = scrape_with_api(query, API_KEY)
    
    for i, place in enumerate(results, 1):
        print(f"\n{i}. {place['name']}")
        print(f"   Address: {place['address']}")
        print(f"   Phone: {place['phone']}")
        print(f"   Rating: {place['rating']} ({place['reviews_count']} reviews)")
        print(f"   Website: {place['website']}")