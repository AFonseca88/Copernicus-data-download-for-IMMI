from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def get_coordinates(place_name):
    """
    Returns (lat, lon) for a given place name using OpenStreetMap (Nominatim).
    Returns None if not found or if an error occurs.
    """
    try:
        # User_agent is required by Nominatim policy
        geolocator = Nominatim(user_agent="copernicus_downloader_app")
        location = geolocator.geocode(place_name)
        
        if location:
            return location.latitude, location.longitude
        else:
            print(f"Localidade '{place_name}' não encontrada.")
            return None
            
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Erro no serviço de geocodificação: {e}")
        return None
