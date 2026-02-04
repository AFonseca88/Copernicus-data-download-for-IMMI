import pandas as pd
import numpy as np

def processar_dados_era5(input_xlsx):
    # 1. Carregar os dados originais
    # Ler ficheiro Excel (engine openpyxl)
    df = pd.read_excel(input_xlsx)
    # Converter time se necessário (geralmente Excel já traz como datetime, mas reforçar é seguro)
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])

    # 2. Cálculos de Conversão
    # Velocidade (m/s -> 0.1 m/s)
    df['ws_ms'] = np.sqrt(df['u10']**2 + df['v10']**2)
    df['ws_ak'] = (df['ws_ms'] * 10).round().astype(int)
    
    # Direção (0-360)
    df['wd_deg'] = (np.degrees(np.arctan2(-df['u10'], -df['v10'])) + 360) % 360
    df.loc[df['ws_ms'] < 0.1, 'wd_deg'] = 0 # Calmo
    df['wd_ak'] = df['wd_deg'].round().astype(int)

    # Temperatura (Kelvin -> Celsius)
    df['t2m_c'] = (df['t2m'] - 273.15).round(1)

    # Estabilidade (Klug/Manier)
    def calc_km(row):
        is_day = row['ssr'] > 10
        octas = row['tcc'] * 8
        ws = row['ws_ms']
        if not is_day:
            return 1 if octas <= 2 else 2 if octas <= 5 else 3
        else:
            if row['ssr'] > 200:
                return 6 if ws < 2.0 else 5 if ws < 3.0 else 4
            return 3
    
    df['km_class'] = df.apply(calc_km, axis=1)

    # Chuva (0.1 mm)
    df['prec_ak'] = (df['tp'] * 10000).round().astype(int)

    # 3. Exportar para EXCEL
    df_excel = df[['time', 't2m_c', 'wd_ak', 'ws_ak', 'km_class', 'prec_ak']].copy()
    df_excel.columns = ['Data/Hora', 'Temp (C)', 'Dir Vento (deg)', 'Vel Vento (0.1 m/s)', 'Estabilidade (KM)', 'Prec (0.1 mm)']
    df_excel.to_excel('data/processed/dados_tratados_akterm.xlsx', index=False)

    # 4. Exportar para AKTerm
    lines = [
        "* AKTerm criado a partir de dados ERA5",
        f"* Periodo: {df['time'].min().strftime('%d.%m.%Y')} - {df['time'].max().strftime('%d.%m.%Y')}",
        "+ Anemometerhoehen (0.1 m):   100   100   100   100   100   100   100   100   100"
    ]

    for _, row in df.iterrows():
        t = row['time']
        # Estrutura de 18 colunas conforme ficheiro de exemplo
        linha = (f"AK 11111 {t.year} {t.month:02d} {t.day:02d} {t.hour:02d} 00 "
                 f"1 1 {int(row['wd_ak']):3d} {int(row['ws_ak']):3d} "
                 f"1 {int(row['km_class'])} 1 -999 9 {int(row['prec_ak']):3d} 1")
        lines.append(linha)

    with open('data/processed/dados_era5.akterm', 'w') as f:
        f.write("\n".join(lines) + "\n")

