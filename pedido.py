import calendar

def get_request_params(year, month, area):
    """
    Returns the dataset name and the request dictionary for a specific year, month, and area.
    Automatically adjusts the days based on the month and year (leap years).

    Args:
        year (str or int): The year (e.g., "2025").
        month (str or int): The month (e.g., "01" or 1).
        area (list): The area bounding box [North, West, South, East].

    Returns:
        tuple: (dataset_name, request_dictionary)
    """
    dataset = "reanalysis-era5-single-levels"
    
    # Ensure year and month are strings for the request
    year_str = str(year)
    
    # Ensure month is formatted as two digits for the request (e.g. "01")
    if isinstance(month, int):
        month_str = f"{month:02d}"
    else:
        month_str = month
        
    # Calculate number of days in the month
    try:
        # calendar.monthrange returns (weekday_of_first_day, number_of_days)
        _, num_days = calendar.monthrange(int(year), int(month_str))
        days = [f"{d:02d}" for d in range(1, num_days + 1)]
    except ValueError as e:
        print(f"Error calculating days: {e}")
        # Fallback or re-raise
        raise e

    request = {
        "product_type": ["reanalysis"],
        "variable": [
            "total_cloud_cover",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "2m_temperature",
            "total_precipitation",
            "surface_net_solar_radiation"
        ],
        "year": [year_str],
        "month": [month_str],
        "day": days,
        "time": [
            "00:00", "01:00", "02:00",
            "03:00", "04:00", "05:00",
            "06:00", "07:00", "08:00",
            "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00",
            "15:00", "16:00", "17:00",
            "18:00", "19:00", "20:00",
            "21:00", "22:00", "23:00"
        ],
        "data_format": "grib",
        "download_format": "unarchived",
        "area": area
    }
    
    return dataset, request
