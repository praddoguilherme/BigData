Coleta, Inserção e Previsão de Dados Meteorológicos

Este projeto envolve três componentes principais:

1. Coleta e inserção de dados meteorológicos em tempo real no banco de dados MySQL**.
2. Inserção de dados históricos meteorológicos obtidos de uma API externa**.
3. Modelo preditivo de Machine Learning para previsão de precipitação com base em dados de temperatura e umidade**.

Estrutura do Projeto

- `coleta_insercao_mysql.py`: Script responsável pela coleta de dados meteorológicos atuais e sua inserção em um banco de dados MySQL. Ele também realiza backups automáticos do banco de dados.
- `coleta_dados_historicos.py`: Script para obter dados meteorológicos históricos de uma API em formato JSON e inseri-los no banco de dados MySQL.
- `predict.py`: Script que implementa um modelo de aprendizado de máquina (Random Forest Regressor) para prever precipitação com base nos dados coletados.

Pré-requisitos

Certifique-se de que as seguintes dependências estão instaladas:

- Python 3.x
- MySQL
- Bibliotecas Python:
  - `requests`
  - `mysql-connector-python`
  - `scikit-learn`
  - `pandas`
  - `numpy`
  - `tenacity`
  - `logging`

Configuração

Banco de Dados MySQL

1. Criação do Banco de Dados**: Crie o banco de dados MySQL que será utilizado para armazenar os dados meteorológicos (atuais e históricos).

2. Variáveis de Ambiente**: Configure a senha do MySQL em uma variável de ambiente chamada `MYSQL_PASSWORD` para o script de coleta em tempo real (`coleta_insercao_mysql.py`).

3. Tabelas**: As tabelas necessárias devem ser criadas no banco de dados MySQL com os seguintes campos:

   ```sql
   CREATE TABLE dados_meteorologicos (
       data DATETIME,
       temperatura FLOAT,
       umidade FLOAT,
       precipitacao FLOAT
   );
   
   CREATE TABLE dados_climaticos2 (
       data DATETIME,
       temperatura FLOAT,
       precipitacao FLOAT,
       umidade FLOAT
   );
   ```

Instalação das Dependências

Instale as bibliotecas Python necessárias executando:

```bash
pip install -r requirements.txt
```

Configuração dos Caminhos de Arquivos

No script `coleta_dados_historicos.py`, ajuste o caminho para o arquivo JSON que contém os dados históricos (`dados_meteo.json`), ou forneça o caminho correto caso o arquivo esteja armazenado localmente.

Uso

Coleta de Dados em Tempo Real e Inserção no MySQL

Para coletar os dados meteorológicos atuais e inseri-los no banco de dados, execute:

```bash
python coleta_insercao_mysql.py
```

Este script:
- Verifica a conexão com a internet.
- Faz backup do banco de dados antes de inserir novos dados.
- Coleta e insere os dados no banco de dados.

Coleta e Inserção de Dados Históricos

Para obter e inserir dados meteorológicos históricos no banco de dados, execute:

```bash
python coleta_dados_historicos.py
```

Este script:
- Lê os dados históricos de um arquivo JSON.
- Processa e insere os dados no banco de dados MySQL.

Execução do Modelo Preditivo

Para treinar o modelo de Machine Learning e realizar previsões, execute:

```bash
python predict.py
```

Este script:
- Carrega os dados meteorológicos.
- Treina um modelo de regressão usando RandomForest.
- Gera previsões e as salva em um arquivo CSV (`previsoes_resultados.csv`).

Logs

- O log de coleta e inserção de dados em tempo real está em `coleta_insercao.log`.
- O log de coleta de dados históricos está em `coleta_insercao_historico.log`.

Estrutura de Arquivos

- `coleta_insercao_mysql.py`: Script de coleta de dados meteorológicos em tempo real.
- `coleta_dados_historicos.py`: Script para inserção de dados históricos de uma API no banco de dados.
- `predict.py`: Script para previsão de precipitação usando aprendizado de máquina.
- `coleta_insercao.log`: Logs das operações de coleta e inserção de dados em tempo real.
- `coleta_insercao_historico.log`: Logs das operações de inserção de dados históricos.
- `previsoes_resultados.csv`: Resultados das previsões geradas pelo modelo de Machine Learning.

Considerações Finais

Este projeto faz parte de um estudo sobre Big Data, focando na coleta e inserção de dados meteorológicos, além de previsões climáticas utilizando aprendizado de máquina. As etapas de coleta, armazenamento e modelagem são totalmente integradas.
