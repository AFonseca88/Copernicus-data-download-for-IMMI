import os
import xarray as xr
import pandas as pd
import glob
import cfgrib
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

def listar_ficheiros_grib(diretorio="data"):
    """
    Retorna uma lista de ficheiros .grib no diretório especificado.
    """
    return glob.glob(os.path.join(diretorio, "*.grib"))

def processar_variaveis_atm(datasets):
    """
    Processa variáveis atmosféricas (Grupo 1): t2m, u10, v10, tcc.
    Retorna um DataFrame unificado.
    """
    nome_grupo = "Atmosferico"
    vars_desejadas = ['t2m', 'u10', 'v10', 'tcc', 'blh']
    print(f"\n--- A processar grupo: {nome_grupo} {vars_desejadas} ---")
    
    dfs_encontrados = []
    
    for var in vars_desejadas:
        for ds in datasets:
            if var in ds.data_vars:
                # Extrair variável e converter para DF
                v_df = ds[var].to_dataframe().reset_index()
                
                # Normalizar colunas imediatamente
                if 'time' not in v_df.columns:
                    tempo_possivel = [c for c in v_df.columns if 'time' in c or 'valid_time' in c]
                    if tempo_possivel: v_df = v_df.rename(columns={tempo_possivel[0]: 'time'})
                
                if 'latitude' not in v_df.columns and 'lat' in v_df.columns:
                    v_df = v_df.rename(columns={'lat': 'latitude'})
                if 'longitude' not in v_df.columns and 'lon' in v_df.columns:
                    v_df = v_df.rename(columns={'lon': 'longitude'})
                
                # Manter apenas chaves e a variável
                chaves = ['time', 'latitude', 'longitude']
                cols_para_manter = chaves + [var]
                disponiveis = [c for c in cols_para_manter if c in v_df.columns]
                
                dfs_encontrados.append(v_df[disponiveis])
                break # Encontrou a variável, passa para a próxima

    if not dfs_encontrados:
        print(f"  Nenhuma variável do grupo encontrada.")
        return pd.DataFrame() # Retorna vazio

    # Merge de todos os dataframes encontrados
    df_final = dfs_encontrados[0]
    chaves_merge = ['time', 'latitude', 'longitude']
    
    for i in range(1, len(dfs_encontrados)):
        # Verificar quais chaves de merge existem em ambos
        chaves_atuais = [k for k in chaves_merge if k in df_final.columns and k in dfs_encontrados[i].columns]
        df_final = pd.merge(df_final, dfs_encontrados[i], on=chaves_atuais, how='inner')
    
    return df_final

def processar_variaveis_fluxo(datasets):
    """
    Processa variáveis de fluxo/acumuladas (Grupo 2): tp, ssr.
    Retorna um DataFrame unificado apenas com valid_time e as variáveis.
    """
    nome_grupo = "Fluxo/Acumulado"
    vars_desejadas = ['tp', 'ssr']
    print(f"\n--- A processar grupo: {nome_grupo} {vars_desejadas} ---")
    
    dfs_encontrados = []
    
    for var in vars_desejadas:
        for ds in datasets:
            if var in ds.data_vars:
                # Extrair variável e converter para DF
                v_df = ds[var].to_dataframe().reset_index()
                
                # Verificar valid_time
                if 'valid_time' in v_df.columns:
                    # Manter apenas valid_time e a variável
                    v_df = v_df[['valid_time', var]]
                    dfs_encontrados.append(v_df)
                else:
                    # Fallback se valid_time não existir (tenta time padrão)
                    print(f"  Aviso: 'valid_time' não encontrado para {var}. A tentar 'time'.")
                    if 'time' in v_df.columns:
                         v_df = v_df.rename(columns={'time': 'valid_time'})
                         v_df = v_df[['valid_time', var]]
                         dfs_encontrados.append(v_df)
                    
                break # Encontrou a variável, passa para a próxima

    if not dfs_encontrados:
        print(f"  Nenhuma variável do grupo encontrada.")
        return pd.DataFrame() # Retorna vazio

    # Merge de todos os dataframes encontrados
    df_final = dfs_encontrados[0]
    chaves_merge = ['valid_time']
    
    for i in range(1, len(dfs_encontrados)):
        # Verificar quais chaves de merge existem em ambos
        chaves_atuais = [k for k in chaves_merge if k in df_final.columns and k in dfs_encontrados[i].columns]
        df_final = pd.merge(df_final, dfs_encontrados[i], on=chaves_atuais, how='outer') # outer merge para manter todos os passos
    
    # --- FILTRAGEM POR MÊS PREDOMINANTE ---
    if not df_final.empty and 'valid_time' in df_final.columns:
        # Garantir datetime
        df_final['valid_time'] = pd.to_datetime(df_final['valid_time'])
        
        # Criar coluna auxiliar para o mês (Ano-Mês)
        df_final['chave_mes'] = df_final['valid_time'].dt.to_period('M')
        
        # Contar ocorrências por mês
        contagens_mes = df_final['chave_mes'].value_counts()
        
        if not contagens_mes.empty:
            # Identificar o mês com mais dados
            mes_mais_frequente = contagens_mes.idxmax()
            contagem = contagens_mes.max()
            
            print(f"  Analise de meses: {contagens_mes.to_dict()}")
            print(f"  Mês selecionado (mais dados): {mes_mais_frequente} ({contagem} registos)")
            
            # Filtrar
            len_inicial = len(df_final)
            df_final = df_final[df_final['chave_mes'] == mes_mais_frequente].copy()
            df_final = df_final.drop(columns=['chave_mes'])
            
            removidos = len_inicial - len(df_final)
            if removidos > 0:
                print(f"  Registos de outros meses removidos: {removidos}")
        
    return df_final

def processar_ficheiro(caminho_ficheiro, diretorio_saida="data/processed"):
    
    """
    Lê um ficheiro GRIB e converte para CSV, lidando com múltiplas mensagens GRIB.
    """
    try:
        print(f"A processar ficheiro: {caminho_ficheiro}...")
        
        # cfgrib.open_datasets retorna uma lista de datasets
        datasets = cfgrib.open_datasets(caminho_ficheiro)
        
        if not datasets:
            print(f"Aviso: Nenhuns dados encontrados em {caminho_ficheiro}")
            return None, None

        print(f"Num datasets encontrados: {len(datasets)}")
        
        # Grupo 1: Atmosférico/Instantâneo
        df_atm = processar_variaveis_atm(datasets)
        
        # Grupo 2: Acumulado/Fluxo
        df_flux = processar_variaveis_fluxo(datasets)

        # Fechar datasets para libertar bloqueios (necessário para apagar .idx)
        for ds in datasets:
            ds.close()

        return df_atm, df_flux

    except Exception as e:
        print(f"Erro ao processar {caminho_ficheiro}: {e}")
        return None, None
    finally:
        # Cleanup dos ficheiros .idx gerados pelo cfgrib
        try:
            # O padrão é algo como nome.grib.923a8.idx
            padrao_idx = caminho_ficheiro + "*.idx"
            indexes_encontrados = glob.glob(padrao_idx)
            for idx in indexes_encontrados:
                try:
                    os.remove(idx)
                    # print(f"  Ficheiro de índice removido: {idx}")
                except Exception as erro_del:
                    print(f"  Aviso: Não foi possível remover {idx}: {erro_del}")
        except Exception as e:
            pass

def processar_tudo():
    """
    Encontra e processa todos os ficheiros GRIB.
    Acumula os dados e gera um único ficheiro Excel (.xlsx) final com variáveis atmosféricas e de fluxo combinadas.
    """
    ficheiros = listar_ficheiros_grib()
    
    if not ficheiros:
        print("Nenhum ficheiro .grib encontrado na pasta data.")
        return

    print(f"Encontrados {len(ficheiros)} ficheiros .grib.")
    
    # Criar pasta data/processed se não existir
    if not os.path.exists("data/processed"):
        os.makedirs("data/processed")
    else:
        # Remover ficheiro final antigo se existir (xlsx ou csv antigo)
        for f_antigo in ["data/processed/dados_finais.xlsx", "data/processed/dados_finais.csv"]:
            if os.path.exists(f_antigo):
                try:
                    os.remove(f_antigo)
                    print(f"Cleanup: {f_antigo} removido antes de iniciar processamento.")
                except:
                    pass

    lista_atm = []
    lista_flux = []
    
    for f in ficheiros:
        # Processar ficheiro
        resultado = processar_ficheiro(f)
        
        if resultado is None:
            continue

        # Desempacotar resultados
        df_atm_novo, df_flux_novo = resultado
        
        if df_atm_novo is not None and not df_atm_novo.empty:
            lista_atm.append(df_atm_novo)
            
        if df_flux_novo is not None and not df_flux_novo.empty:
            lista_flux.append(df_flux_novo)

    # --- Consolidação e Merge Final ---
    df_atm_total = pd.DataFrame()
    df_flux_total = pd.DataFrame()

    if lista_atm:
        df_atm_total = pd.concat(lista_atm, ignore_index=True)
        # Garantir datetime em 'time'
        if 'time' in df_atm_total.columns:
            df_atm_total['time'] = pd.to_datetime(df_atm_total['time'])

    if lista_flux:
        df_flux_total = pd.concat(lista_flux, ignore_index=True)
        # Garantir datetime em 'valid_time' e renomear para 'time' para o merge
        if 'valid_time' in df_flux_total.columns:
            df_flux_total['valid_time'] = pd.to_datetime(df_flux_total['valid_time'])
            df_flux_total = df_flux_total.rename(columns={'valid_time': 'time'})

    # Verificar se temos dados para combinar
    if not df_atm_total.empty and not df_flux_total.empty:
        print("\n--- A combinar dados atmosféricos e de fluxo ---")
        
        df_final = pd.merge(df_atm_total, df_flux_total, on='time', how='inner')
        
        caminho_saida = "data/processed/dados_finais.xlsx"
        print(f"A guardar ficheiro Excel em: {caminho_saida} ...")
        df_final.to_excel(caminho_saida, index=False)
        print(f"Ficheiro final combinado guardado com sucesso.")
        print(f"Total de registos: {len(df_final)}")
        
    elif not df_atm_total.empty:
        print("\nApenas dados atmosféricos disponíveis.")
        df_atm_total.to_excel("data/processed/dados_finais_atm.xlsx", index=False)
        
    elif not df_flux_total.empty:
        print("\nApenas dados de fluxo disponíveis.")
        df_flux_total.to_excel("data/processed/dados_finais_flux.xlsx", index=False)

    print("\nProcessamento concluído.")
