from src.downloader import executar_download, verificar_cdsapirc
from src.geocoder import obter_coordenadas
from src.process_grib import processar_tudo
from src.conversor_akterm import processar_dados_era5
import sys
import os
import shutil
import stat
import time

ANO_ALVO = "2025"
MESES_ALVO = {"01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"}

def menu_download():
    """
    Executa a interação com o utilizador para o download.
    Retorna True se o download foi executado, False caso contrário.
    """
    meses_alvo = MESES_ALVO
    localidade = input("Introduza a localidade (Enter para Viseu): ")

    print("Introduza o ano dos dados: (se vazio, assume 2025)")
    input_ano = input()

    if not input_ano.strip():
        ano_atual = "2025"
    else:
        ano_atual = input_ano.strip()

    print("Introduza o mês (1-12) ou deixe vazio para todos os meses:")
    input_mes = input()
    
    if input_mes.strip():
        try:
             mes_int = int(input_mes.strip())
             if 1 <= mes_int <= 12:
                 meses_alvo = {f"{mes_int:02d}"}
             else:
                 print("Mês inválido. A selecionar todos os meses.")
        except ValueError:
             print("Entrada inválida. A selecionar todos os meses.")

    lat = None
    lon = None

    if not localidade.strip():
        print("Localidade vazia. A assumir Viseu.")
        lat, lon = 40.66, -7.91
    else:
        coords = obter_coordenadas(localidade)
        if coords:
            lat, lon = coords
        else:
            print("Não foi possível obter coordenadas via API.")
            return False

    if lat is not None and lon is not None:
        # Resumo
        nome_local = localidade.strip() if localidade.strip() else 'Viseu'
        print("\n--- RESUMO ---")
        print(f"Localidade: {nome_local}")
        print(f"Coordenadas: Lat {lat}, Lon {lon}")
        print(f"Ano: {ano_atual}")
        print(f"Meses: {len(meses_alvo)} meses selecionados ({', '.join(sorted(list(meses_alvo)))})")
        print("------------------------")

        confirmar = input("Deseja prosseguir com o download? (s/n): ")

        if confirmar.lower() == 's':
            print(f"\nA iniciar download para {nome_local}...")

            meses_ordenados = sorted(list(meses_alvo))

            for mes in meses_ordenados:
                executar_download(ano_atual, mes, lat, lon, nome_local)
            return True
        else:
            print("Operação cancelada.")
            return False
    return False

def limpar_dados():
    """
    Remove todos os ficheiros e subdiretórios da pasta 'data'.
    Pede confirmação ao utilizador.
    """
    pasta_dados = 'data'
    
    if not os.path.exists(pasta_dados):
        print(f"A pasta '{pasta_dados}' não existe. Nada a limpar.")
        return

    print("\n!!! ATENÇÃO !!!")
    print(f"Esta ação irá APAGAR PERMANENTEMENTE todos os ficheiros em '{pasta_dados}'.")
    confirmacao = input("Tem a certeza que deseja continuar? (escreva 'sim' para confirmar): ")

    if confirmacao.lower() == 'sim':
        
        def on_rm_error(func, path, exc_info):
            # Tenta alterar permissões e re-executar
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception as e:
                print(f"  Não foi possível apagar {path}: {e}")

        try:
            print("A limpar dados...")
            # Opção 1: Remover a pasta e recriá-la
            if os.path.exists(pasta_dados):
                # Tenta apagar até 3 vezes (Windows pode ter delays em libertar handles)
                for i in range(3):
                    try:
                        shutil.rmtree(pasta_dados, onerror=on_rm_error)
                        break
                    except Exception as e:
                        if i < 2:
                            time.sleep(1) # Espera 1 segundo e tenta de novo
                        else:
                            raise e
            
            # Recriar pasta vazia
            if not os.path.exists(pasta_dados):
                os.makedirs(pasta_dados)
                
            print("Todos os dados foram apagados com sucesso.")
        except Exception as e:
            print(f"Erro ao limpar dados: {e}")
            print("Algum ficheiro pode estar a ser usado por outro programa.")
    else:
        print("Operação cancelada.")

def main():
    # Verificar configuração da API antes de iniciar
    ok, msg = verificar_cdsapirc()
    if not ok:
        print("\n!!! ERRO DE CONFIGURAÇÃO !!!")
        print(msg)
        print("-" * 50)
        print("Para utilizar este programa, necessita de uma conta no Copernicus CDS.")
        print("1. Registe-se em: https://cds.climate.copernicus.eu/")
        print("2. Obtenha a sua chave de API e URL.")
        print("3. Crie um ficheiro chamado '.cdsapirc' na pasta do programa ou na sua pasta de utilizador.")
        print("   O ficheiro deve conter:")
        print("   url: https://cds.climate.copernicus.eu/api")
        print("   key: {UID}:{API_KEY}")
        print("-" * 50)
        input("Pressione Enter para sair...")
        sys.exit()

    while True:
        print("\n--- MENU ---")
        print("1. Processamento Completo (Download -> GRIB -> XLSX -> AKTerm)")
        print("2. Download dados")
        print("3. Processar dados GRIB (.grib -> .xlsx)")
        print("4. Processar dados AKTerm (.xlsx -> .akterm)")
        print("5. Limpar todos os dados")
        print("6. Sair")
    
        escolha = input("Escolha uma opção: ")
    
        if escolha == "1":
            print("--- INICIANDO PROCESSAMENTO COMPLETO ---")
            
            # Passo 0: Download
            if menu_download():
                # Passo 1: GRIB -> XLSX
                processar_tudo()
                
                # Passo 2: XLSX -> AKTerm
                xlsx_path = 'data/processed/dados_finais.xlsx'
                if os.path.exists(xlsx_path):
                    print("A processar para AKTerm...")
                    processar_dados_era5(xlsx_path)
                    print("Processamento completo concluído.")
                else:
                    print("Erro: Falha na etapa GRIB -> XLSX. Ficheiro Excel não gerado.")
            else:
                 print("Processamento completo cancelado pelo utilizador na etapa de download.")

        elif escolha == "2":
            menu_download()
    
        elif escolha == "3":
            processar_tudo()

        elif escolha == "4":
            xlsx_path = 'data/processed/dados_finais.xlsx'
            if os.path.exists(xlsx_path):
                print("A converter dados para AKTerm...")
                processar_dados_era5(xlsx_path)
                print("Conversão concluída.")
            else:
                print(f"Erro: Ficheiro {xlsx_path} não encontrado. Execute a opção 1 ou 3 primeiro.")

        elif escolha == "5":
            limpar_dados()

        elif escolha == "6":
            print("A sair...")
            sys.exit()
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
