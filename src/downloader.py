import cdsapi
import os
from src.pedido_ERA5 import obter_parametros_pedido

def configurar_cliente():
    """Configura o cliente CDS API usando configuração local se disponível."""
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # Verificar em src/
    config_local = os.path.join(diretorio_atual, '.cdsapirc')
    
    # Verificar na raiz do projeto (pai de src/)
    config_raiz = os.path.join(os.path.dirname(diretorio_atual), '.cdsapirc')

    if os.path.exists(config_local):
        os.environ['CDSAPI_RC'] = config_local
    elif os.path.exists(config_raiz):
        os.environ['CDSAPI_RC'] = config_raiz
        
    return cdsapi.Client()

def calcular_area(lat, lon, margem=0.1):
    """
    Calcula a caixa delimitadora [Norte, Oeste, Sul, Este] com uma margem dada.
    """
    return [lat + margem, lon - margem, lat - margem, lon + margem]

def executar_download(ano, mes, lat, lon):
    """
    Orquestra o processo de download.
    """
    cliente = configurar_cliente()

    area_alvo = calcular_area(lat, lon)
    
    # Garantir que o diretório de saída existe
    diretorio_saida = "data"
    os.makedirs(diretorio_saida, exist_ok=True)
    
    ficheiro_saida = os.path.join(diretorio_saida, f"download_{ano}_{mes}.grib")
    
    nome_dataset, parametros = obter_parametros_pedido(ano, mes, area_alvo)
    
    print(f"A iniciar download de {nome_dataset}...")
    print(f"Ficheiro de saída: {ficheiro_saida}")
    
    try:
        cliente.retrieve(nome_dataset, parametros, ficheiro_saida)
        print(f"Download concluído! Ficheiro guardado em: {ficheiro_saida}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
