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

def verificar_cdsapirc():
    """
    Verifica se o ficheiro .cdsapirc existe e contém as chaves necessárias.
    Retorna (True, None) se ok, ou (False, mensagem_erro).
    """
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    config_local = os.path.join(diretorio_atual, '.cdsapirc')
    config_raiz = os.path.join(os.path.dirname(diretorio_atual), '.cdsapirc')
    
    caminho_final = None
    if os.path.exists(config_local):
        caminho_final = config_local
    elif os.path.exists(config_raiz):
        caminho_final = config_raiz
        
    if not caminho_final:
        return False, "Ficheiro .cdsapirc não encontrado. É necessário configurar a chave da API do Copernicus."

    try:
        with open(caminho_final, 'r') as f:
            conteudo = f.read()
            
            # Verificação completa linha a linha
            lines = [l.strip() for l in conteudo.splitlines()]
            
            tem_url = False
            tem_key = False
            
            for l in lines:
                if l.startswith('url:'):
                    parts = l.split(':', 1)
                    if len(parts) > 1 and parts[1].strip():
                        tem_url = True
                elif l.startswith('key:'):
                    parts = l.split(':', 1)
                    if len(parts) > 1:
                        key_val = parts[1].strip()
                        # Verifica se não é vazio e se não é o placeholder [ENCRYPTION_KEY]
                        if key_val and key_val != "[ENCRYPTION_KEY]":
                            tem_key = True
            
            if not tem_url:
                 return False, f"Ficheiro {caminho_final} sem URL válido."
            if not tem_key:
                 return False, f"Ficheiro {caminho_final} sem KEY válida (não pode ser vazia ou '[ENCRYPTION_KEY]')."
                 
    except Exception as e:
        return False, f"Erro ao ler .cdsapirc: {e}"

    return True, "Configuração válida."

def calcular_area(lat, lon, margem=0.1):
    """
    Calcula a caixa delimitadora [Norte, Oeste, Sul, Este] com uma margem dada.
    """
    return [lat + margem, lon - margem, lat - margem, lon + margem]

def executar_download(ano, mes, lat, lon, nome_local="local"):
    """
    Orquestra o processo de download.
    """
    cliente = configurar_cliente()

    area_alvo = calcular_area(lat, lon)
    
    # Garantir que o diretório de saída existe
    diretorio_saida = "data"
    os.makedirs(diretorio_saida, exist_ok=True)
    
    # Formato solicitado: local_ano_mês
    ficheiro_saida = os.path.join(diretorio_saida, f"{nome_local}_{ano}_{mes}.grib")
    
    nome_dataset, parametros = obter_parametros_pedido(ano, mes, area_alvo)
    
    print(f"A iniciar download de {nome_dataset}...")
    print(f"Ficheiro de saída: {ficheiro_saida}")
    
    try:
        cliente.retrieve(nome_dataset, parametros, ficheiro_saida)
        print(f"Download concluído! Ficheiro guardado em: {ficheiro_saida}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
