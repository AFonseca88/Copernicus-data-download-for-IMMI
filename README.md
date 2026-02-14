# Copernicus CDS Data Downloader

Este projeto permite fazer o download de dados do Copernicus Climate Data Store (CDS) usando a API oficial, processá-los para formato Excel e convertê-los para o formato AKTerm, para a utilização no IMMI.

## Funcionalidades

1.  **Download**: Descarrega dados ERA5 (reanalysis) para variáveis atmosféricas e de fluxo.
2.  **Processamento**:
    *   Filtra os dados grib recebidos.
    *   Consolida ficheiros mensais num único ficheiro anual.
    *   Gera um ficheiro **Excel (.xlsx)** com os dados combinados e alinhados temporalmente.
3.  **Conversão AKTerm**:
    *   Converte os dados do Excel para o formato `.akterm` usado em modelação.
    *   Calcula variáveis derivadas como velocidade/direção do vento, classes de estabilidade e precipitação.

## Pré-requisitos

1.  **Conta no Copernicus CDS**: Registe-se em [https://cds.climate.copernicus.eu/](https://cds.climate.copernicus.eu/).
2.  **Chave de API**:
    *   Faça login no portal CDS e obtenha a sua `URL` e `API Key`.
    *   Configure o ficheiro `.cdsapirc` na raiz do projeto com o formato:
        ```text
        url: https://cds.climate.copernicus.eu/api/v2
        key: UID:API_KEY
        ```

## Instalação

1.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Utilização

Execute o script principal para aceder ao menu interativo:

```bash
python main.py
```

### Opções do Menu:
1.  **Processamento Completo (Download -> GRIB -> XLSX -> AKTerm)**: Executa todo o fluxo sequencialmente.
2.  **Download dados**: Pede a localidade e ano, e descarrega os ficheiros .grib mensais.
3.  **Processar dados GRIB (.grib -> .xlsx)**: Lê todos os ficheiros .grib da pasta `data`, processa, filtra e gera o ficheiro `data/processed/dados_finais.xlsx`.
4.  **Processar dados AKTerm (.xlsx -> .akterm)**: Converte o ficheiro Excel gerado anteriormente para `data/processed/dados_era5.akterm`.
5.  **Limpar todos os dados**: Remove todo o conteúdo da pasta `data/`.
6.  **Sair**: Fecha o programa.

---

## Dados Transferidos (ERA5)

O programa descarrega dados do dataset `reanalysis-era5-single-levels` com frequência horária.

| Sigla | Variável (Nome Oficial) | Descrição | Unidade Original |
| :--- | :--- | :--- | :--- |
| **t2m** | 2m temperature | Temperatura do ar a 2 metros de altura | Kelvin (K) |
| **u10** | 10m u-component of wind | Componente U (Este-Oeste) do vento a 10m | m/s |
| **v10** | 10m v-component of wind | Componente V (Norte-Sul) do vento a 10m | m/s |
| **tcc** | Total cloud cover | Cobertura total de nuvens | Fração (0-1) |
| **tp** | Total precipitation | Precipitação total acumulada | Metros (m) |
| **ssr** | Surface net solar radiation | Radiação solar líquida na superfície (acumulada) | J/m² |
| **blh** | Boundary layer height | Altura da camada limite planetária | Metros (m) |

---

## Dados de Saída e Unidades

O ficheiro final para modelação (`dados_era5.akterm` e o Excel intermédio `dados_tratados_akterm.xlsx`) contém as seguintes colunas processadas:

| Campo (Excel) | Variável AKTerm | Unidade Final | Descrição |
| :--- | :--- | :--- | :--- |
| **Data/Hora** | (Cabeçalho) | - | Data e hora da observação |
| **Temp (C)** | Coluna 14 (aprox) | **°C** (Graus Celsius) | Temperatura convertida |
| **Dir Vento (deg)** | Coluna 4 | **Graus** (0-360) | Direção de onde sopra o vento |
| **Vel Vento (0.1 m/s)** | Coluna 5 | **0.1 m/s** | Velocidade escalada (ex: 50 = 5.0 m/s) |
| **Estabilidade (KM)** | Coluna 6 | **Classe (1-6)** | Classe de estabilidade Klug/Manier |
| **Prec (0.1 mm)** | Coluna 8 (aprox) | **0.1 mm** | Precipitação escalada (ex: 10 = 1.0 mm) |
| **BLH (m)** | Coluna 7 (aprox) | **Metros** | Altura da camada de mistura |

---

## Cálculos e Conversões

O módulo `src/conversor_akterm.py` realiza as seguintes transformações:

1.  **Temperatura**:
    *   $T(^\circ C) = T(K) - 273.15$

2.  **Vento (Velocidade e Direção)**:
    *   **Velocidade ($m/s$)**: $\sqrt{u10^2 + v10^2}$
    *   **Velocidade AKTerm**: Multiplicada por 10 e arredondada (formato inteiro decimétrico).
    *   **Direção**: Calculada com `atan2(-u10, -v10)` para obter a direção *de onde* sopra o vento (meteorológica). Convertida para 0-360º.
    *   **Calmaria**: Se a velocidade < 0.1 m/s, a direção é definida como 0.

3.  **Precipitação**:
    *   Convertida de metros (m) para 0.1 milímetros.
    *   Fator de conversão: $\text{Valor} \times 10000$ (já que $1 m = 1000 mm$ e queremos décimas de mm).

4.  **Classes de Estabilidade (Klug/Manier)**:
    *   Estimada com base na **Carga Térmica (Dia/Noite)**, **Velocidade do Vento** e **Nebulosidade**.
    *   A classe varia de **1 (Muito Estável)** a **6 (Muito Instável)**.
    
    | Condição | Critério (Radiação/Nuvens) | Critério Adicional (Vento) | Classe Resultante | Descrição |
    | :--- | :--- | :--- | :---: | :--- |
    | **Noite** | SSR $\le$ 10 W/m² | Nuvens $\le$ 2/8 (Céu Limpo) | **1** | Muito Estável |
    | **Noite** | SSR $\le$ 10 W/m² | Nuvens $\le$ 5/8 | **2** | Estável |
    | **Noite** | SSR $\le$ 10 W/m² | Nuvens > 5/8 (Nublado) | **3** | Neutra (Noturna) |
    | **Dia** | 10 < SSR $\le$ 200 W/m² | (Independente) | **3** | Neutra (Diurna)/Fraca Insolação |
    | **Dia** | SSR > 200 W/m² (Forte) | Vento < 2.0 m/s | **6** | Muito Instável |
    | **Dia** | SSR > 200 W/m² (Forte) | Vento < 3.0 m/s | **5** | Instável |
    | **Dia** | SSR > 200 W/m² (Forte) | Vento $\ge$ 3.0 m/s | **4** | Ligeiramente Instável |
