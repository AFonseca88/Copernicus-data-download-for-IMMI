from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def obter_coordenadas(nome_local):
    """
    Retorna (lat, lon) para um nome de local dado usando OpenStreetMap (Nominatim).
    Retorna None se não encontrado ou se ocorrer um erro.
    """
    try:
        # User_agent é obrigatório pela política do Nominatim
        geolocalizador = Nominatim(user_agent="copernicus_downloader_app")
        localizacao = geolocalizador.geocode(nome_local)
        
        if localizacao:
            return localizacao.latitude, localizacao.longitude
        else:
            print(f"Localidade '{nome_local}' não encontrada.")
            return None
            
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Erro no serviço de geocodificação: {e}")
        return None
