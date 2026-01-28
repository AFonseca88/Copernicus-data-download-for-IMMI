from downloader import run_download

if __name__ == "__main__":
    # --- CONFIGURAÇÃO DO DOWNLOAD ---
    
    # Ano a descarregar
    TARGET_YEAR = "2025"

    # Mês a descarregar (ex: "01" para Janeiro)
    TARGET_MONTH = "01" 
    
    # Coordenadas decimais do ponto de interesse
    # Exemplo: Viseu (aprox.)
    LAT = 40.66
    LON = -7.91
    
    # --------------------------------

    # Executar o download
    run_download(TARGET_YEAR, TARGET_MONTH, LAT, LON)
