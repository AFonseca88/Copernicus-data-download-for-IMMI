from src.downloader import run_download
from src.geocoder import get_coordinates
import sys

# TARGET_YEAR = "2025"
TARGET_MONTHS = {"01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"}

def main():
    target_months = TARGET_MONTHS # Local variable for easier potential future modification
    while True:
        print("\n--- MENU ---")
        print("1. Download dados")
        print("2. Sair")
        
        choice = input("Escolha uma opção: ")
        
        if choice == "1":
            local = input("Introduza a localidade (Enter para Viseu): ")

            print("Introduza o ano dos dados: (se vazio, assume 2025)")
            TARGET_YEAR = input()
            
            if not TARGET_YEAR.strip():
                TARGET_YEAR = "2025"
            
            lat = None
            lon = None

            if not local.strip():
                print("Localidade vazia. A assumir Viseu.")
                # Coordenadas default de Viseu se vazio
                lat, lon = 40.66, -7.91
            else:
                coords = get_coordinates(local)
                if coords:
                    lat, lon = coords
                else:
                    print("Não foi possível obter coordenadas via API.")
                    # Fallback opcional ou loop
                    continue
            
            if lat is not None and lon is not None:
                # Resumo
                local_name = local.strip() if local.strip() else 'Viseu'
                print("\n--- RESUMO ---")
                print(f"Localidade: {local_name}")
                print(f"Coordenadas: Lat {lat}, Lon {lon}")
                print(f"Ano: {TARGET_YEAR}")
                print(f"Meses: {len(target_months)} meses selecionados")
                print("------------------------")
                
                confirm = input("Deseja prosseguir com o download? (s/n): ")
                
                if confirm.lower() == 's':
                    print(f"\nA iniciar download para {local_name}...")
                    
                    # Convert set to sorted list to ensure deterministic order
                    sorted_months = sorted(list(target_months))
                    
                    for month in sorted_months:
                        run_download(TARGET_YEAR, month, lat, lon)
                else:
                    print("Operação cancelada.")
                
        elif choice == "2":
            print("A sair...")
            sys.exit()
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
