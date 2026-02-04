import calendar

def obter_parametros_pedido(ano, mes, area):
    """
    Retorna o nome do dataset e o dicionário de pedido para um ano, mês e área específicos.
    Ajusta automaticamente os dias com base no mês e ano (anos bissextos).

    Args:
        ano (str ou int): O ano (ex: "2025").
        mes (str ou int): O mês (ex: "01" ou 1).
        area (list): A "bounding box" da área [Norte, Oeste, Sul, Este].

    Returns:
        tuple: (nome_dataset, dicionario_pedido)
    """
    nome_dataset = "reanalysis-era5-single-levels"
    
    # Garantir que ano e mês são strings para o pedido
    ano_str = str(ano)
    
    # Garantir que o mês está formatado com dois dígitos (ex: "01")
    if isinstance(mes, int):
        mes_str = f"{mes:02d}"
    else:
        mes_str = mes
        
    # Calcular o número de dias no mês
    try:
        # calendar.monthrange retorna (dia_semana_primeiro_dia, numero_de_dias)
        _, num_dias = calendar.monthrange(int(ano), int(mes_str))
        dias = [f"{d:02d}" for d in range(1, num_dias + 1)]
    except ValueError as e:
        print(f"Erro ao calcular dias: {e}")
        # Fallback ou relançar exceção
        raise e

    pedido = {
        "product_type": ["reanalysis"],
        "variable": [
            "total_cloud_cover",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "2m_temperature",
            "total_precipitation",
            "surface_net_solar_radiation"
        ],
        "year": [ano_str],
        "month": [mes_str],
        "day": dias,
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
    
    return nome_dataset, pedido
