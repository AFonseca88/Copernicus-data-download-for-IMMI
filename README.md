# Copernicus CDS Data Downloader

Este projeto permite fazer o download de dados do Copernicus Climate Data Store (CDS) usando a API oficial.

## Pré-requisitos

1.  **Conta no Copernicus CDS**: Registe-se em [https://cds.climate.copernicus.eu/](https://cds.climate.copernicus.eu/).
2.  **Chave de API**:
    *   Faça login no portal CDS.
    *   Vá à sua página de perfil.
    *   Copie a sua `URL` e `API Key`.
3.  **Configuração do Ficheiro `.cdsapirc`**:
    *   O programa já criou um ficheiro `.cdsapirc` na pasta do projeto.
    *   Abra esse ficheiro e substitua o texto `SUBSTITUA_PELO_SEU_UID:SUBSTITUA_PELA_SUA_API_KEY` pela sua chave real (ex: `12345:8b8...`).
    *   Alternativamente, pode mover este ficheiro para a sua pasta de utilizador (`C:\Users\André Fonseca\.cdsapirc`).

## Instalação

1.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Utilização

1.  Abra o ficheiro `main.py` e ajuste os parâmetros `dataset` e `params` conforme necessário.
    *   *Dica*: Pode gerar estes parâmetros no site do CDS usando o botão "Show API request" na página de download dos dados.
2.  Execute o script:
    ```bash
    python main.py
    ```
