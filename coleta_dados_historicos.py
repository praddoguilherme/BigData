import json
from datetime import datetime
import mysql.connector
import logging

logging.basicConfig(
    filename='coleta_insercao_historico.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def ler_dados_historicos_do_arquivo(caminho_arquivo):
    """Lê os dados históricos do arquivo JSON."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados
    except FileNotFoundError:
        logging.error(f"Arquivo {caminho_arquivo} não encontrado.")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar o JSON: {e}")
        return None

def validar_data(ano, mes, dia):
    """Valida se a data é válida para o mês e ano fornecidos."""
    try:
        datetime(ano, mes, dia)
        return True
    except ValueError:
        return False

def processar_e_inserir_dados_historicos(dados, cursor):
    """Processa os dados históricos e insere no banco de dados."""
    if not dados:
        logging.warning("Nenhum dado histórico para processar.")
        return

    ano = 2024 

    for registro in dados['result']:
        mes = registro['month']
        dia = registro['day']

        if not validar_data(ano, mes, dia):
            logging.warning(f"Data inválida: {ano}-{mes}-{dia}. Registro ignorado.")
            continue

        data = datetime(ano, mes, dia).strftime('%Y-%m-%d %H:%M:%S')

        temperatura_kelvin = registro['temp']['mean'] 
        precipitacao = registro['precipitation']['mean'] 
        umidade = registro['humidity']['mean']  

      #######Converter temperatura de Kelvin para Celsius########

        temperatura_celsius = temperatura_kelvin - 273.15

        if temperatura_celsius is not None and umidade is not None and precipitacao is not None:
            try:
                cursor.execute('''
                INSERT INTO dados_climaticos2 (data, temperatura, precipitacao, umidade)
                VALUES (%s, %s, %s, %s)
                ''', (data, temperatura_celsius, precipitacao, umidade))
                logging.info(f"Dados inseridos: {data}, {temperatura_celsius}, {precipitacao}, {umidade}")
            except mysql.connector.Error as err:
                logging.error(f"Erro ao inserir dados: {err}")
        else:
            logging.warning(f"Dados incompletos para a data {data}. Registro ignorado.")

def conectar_e_inserir_dados():
    """Função principal para ler e inserir dados no banco de dados."""
    conn = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Variavel de Ambiente',  
            database='dados_meteorologicos2'  
        )

        cursor = conn.cursor()

        caminho_arquivo = 'dados_meteo.json'

        dados_historicos = ler_dados_historicos_do_arquivo(caminho_arquivo)

        processar_e_inserir_dados_historicos(dados_historicos, cursor)

        conn.commit()
        logging.info("Dados históricos inseridos no banco de dados com sucesso.")
    except mysql.connector.Error as e:
        logging.error(f"Erro ao conectar com o banco de dados MySQL: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    conectar_e_inserir_dados()