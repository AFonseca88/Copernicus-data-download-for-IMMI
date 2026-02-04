# Copernicus CDS Data Downloader

Este projeto permite fazer o download de dados do Copernicus Climate Data Store (CDS) usando a API oficial, processá-los para formato Excel e convertê-los para o formato AKTerm.

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
1.  **Download dados**: Pede a localidade e ano, e descarrega os ficheiros .grib mensais.
2.  **Processar dados GRIB (.grib -> .xlsx)**: Lê todos os ficheiros .grib da pasta `data`, processa, filtra e gera o ficheiro `data/processed/dados_finais.xlsx`.
3.  **Processar dados AKTerm (.xlsx -> .akterm)**: Converte o ficheiro Excel gerado anteriormente para `data/processed/dados_era5.akterm`.
4.  **Processamento Completo**: Executa sequencialmente o processamento GRIB e a conversão AKTerm.
