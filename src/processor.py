import os
import xarray as xr
import pandas as pd
import glob
import cfgrib

def list_grib_files(directory="data"):
    """
    Returns a list of .grib files in the specified directory.
    """
    return glob.glob(os.path.join(directory, "*.grib"))

def process_file(filepath, output_dir="data/processed"):
    """
    Reads a GRIB file and converts it to CSV, handling multiple GRIB messages.
    """
    try:
        print(f"A processar ficheiro: {filepath}...")
        
        # cfgrib.open_datasets returns a list of datasets (one for each hypercube/stepType)
        datasets = cfgrib.open_datasets(filepath)
        
        if not datasets:
            print(f"Aviso: Nenhuns dados encontrados em {filepath}")
            return

        combined_df = pd.DataFrame()

        for i, ds in enumerate(datasets):
            print(f"  - A processar parte {i+1}/{len(datasets)}...")
            try:
                # Convert to DataFrame
                df = ds.to_dataframe().reset_index()
                
                # Normalize time column names
                if 'time1' in df.columns:
                    df = df.rename(columns={'time1': 'time'})
                
                # Ensure time is datetime for proper usage
                if 'time' in df.columns:
                        df['time'] = pd.to_datetime(df['time'])

                if combined_df.empty:
                    combined_df = df
                else:
                    if 'time1' in combined_df.columns:
                        combined_df = combined_df.rename(columns={'time1': 'time'})
                    
                    if 'time' in combined_df.columns:
                            combined_df['time'] = pd.to_datetime(combined_df['time'])

                    # Merge on consistent keys
                    merge_keys = ['time']
                    if 'lat' in df.columns and 'lat' in combined_df.columns:
                        merge_keys.append('lat')
                    elif 'latitude' in df.columns and 'latitude' in combined_df.columns:
                        merge_keys.append('latitude')
                        
                    if 'lon' in df.columns and 'lon' in combined_df.columns:
                        merge_keys.append('lon')
                    elif 'longitude' in df.columns and 'longitude' in combined_df.columns:
                        merge_keys.append('longitude')
                    
                    # Force merge
                    combined_df = pd.merge(combined_df, df, on=merge_keys, how='outer')

            except Exception as e_part:
                print(f"    Erro na parte {i+1}: {e_part}")

        # Clean up duplicates
        if not combined_df.empty and 'time' in combined_df.columns:
             group_keys = ['time']
             if 'lat' in combined_df.columns: group_keys.append('lat')
             elif 'latitude' in combined_df.columns: group_keys.append('latitude')
             
             if 'lon' in combined_df.columns: group_keys.append('lon')
             elif 'longitude' in combined_df.columns: group_keys.append('longitude')
             
             print("  - A consolidar dados duplicados (ex: horas de sobreposição)...")
             combined_df = combined_df.groupby(group_keys).last().reset_index()

        # Create output filename
        filename = os.path.basename(filepath).replace(".grib", ".csv")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        
        # Save to CSV
        combined_df.to_csv(output_path, index=False)
        print(f"Sucesso! Guardado em: {output_path}")
        
    except Exception as e:
        print(f"Erro ao processar {filepath}: {e}")

def process_all():
    """
    Finds and processes all GRIB files.
    """
    files = list_grib_files()
    
    if not files:
        print("Nenhum ficheiro .grib encontrado na pasta data.")
        return

    print(f"Encontrados {len(files)} ficheiros .grib.")
    
    for f in files:
        process_file(f)
    
    print("\nProcessamento concluído.")
