from src.downloader import executar_download
from src.geocoder import obter_coordenadas
from src.process_grib import processar_tudo
from src.conversor_akterm import processar_dados_era5
import sys
import os

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
        print(f"Meses: {len(meses_alvo)} meses selecionados")
        print("------------------------")

        confirmar = input("Deseja prosseguir com o download? (s/n): ")

        if confirmar.lower() == 's':
            print(f"\nA iniciar download para {nome_local}...")

            meses_ordenados = sorted(list(meses_alvo))

            for mes in meses_ordenados:
                executar_download(ano_atual, mes, lat, lon)
            return True
        else:
            print("Operação cancelada.")
            return False
    return False

def main():
    while True:
        print("\n--- MENU ---")
        print("1. Processamento Completo (Download -> GRIB -> XLSX -> AKTerm)")
        print("2. Download dados")
        print("3. Processar dados GRIB (.grib -> .xlsx)")
        print("4. Processar dados AKTerm (.xlsx -> .akterm)")
        print("5. Sair")
    
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
            print("A sair...")
            sys.exit()
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
