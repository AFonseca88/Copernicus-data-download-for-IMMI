import cdsapi
import os
from pedido import get_request_params

def setup_client():
    """Sets up the CDS API client using local config if available."""
    local_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cdsapirc')
    if os.path.exists(local_config):
        os.environ['CDSAPI_RC'] = local_config
    return cdsapi.Client()

def calculate_area(lat, lon, margin=0.1):
    """
    Calculates the bounding box [North, West, South, East] with a given margin.
    """
    return [lat + margin, lon - margin, lat - margin, lon + margin]

def run_download(year, month, lat, lon):
    """
    Orchestrates the download process.
    """
    client = setup_client()

    target_area = calculate_area(lat, lon)
    
    # Ensure output directory exists
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"download_{year}_{month}.grib")
    
    dataset, params = get_request_params(year, month, target_area)
    
    print(f"Starting download for {dataset}...")
    print(f"Output file: {output_file}")
    
    try:
        client.retrieve(dataset, params, output_file)
        print(f"Download complete! File saved to: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
