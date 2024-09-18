import requests
import mysql.connector
import datetime
import logging
import sys
import subprocess
import os
from tenacity import retry, stop_after_attempt, wait_exponential
import json

# Configuração do logging com UTF-8 usando FileHandler
# Obtém a senha do MySQL a partir da variável de ambiente
# FileHandler com encoding UTF-8
# Backup usando mysqldump

logger = logging.getLogger()
logger.setLevel(logging.INFO)


file_handler = logging.FileHandler('coleta_insercao.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def verificar_conexao():
    """Verifica se há conexão com a internet tentando acessar um site confiável."""
    try:
        requests.get('https://www.google.com', timeout=5)
        logging.info("Conexão com a internet verificada com sucesso.")
        return True
    except requests.ConnectionError:
        logging.error("Sem conexão com a internet.")
        return False

def criar_backup():
    """Cria um backup do banco de dados MySQL antes de inserir novos dados."""
    try:
        
        password = os.getenv('MYSQL_PASSWORD')
        if not password:
            raise ValueError("A variável de ambiente MYSQL_PASSWORD não está definida.")

        
        backup_file = f"backup_dados_meteorologicos_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        
        comando = f"mysqldump -u root -p{password} dados_meteorologicos > {backup_file}"
        subprocess.run(comando, shell=True, check=True)
        logging.info(f"Backup do banco de dados criado com sucesso: {backup_file}")
    except Exception as e:
        logging.error(f"Erro ao criar backup do banco de dados: {e}")

# #REMOTO
#         # Comando para criar o backup usando mysqldump
#         comando = f"mysqldump -h 'remote_host' -u root -p{password} dados_meteorologicos > {backup_file}"
#         # Substitua <remote_host> pelo IP ou nome do host do banco de dados remoto
#         subprocess.run(comando, shell=True, check=True)
#         logging.info(f"Backup do banco de dados criado com sucesso: {backup_file}")
#     except Exception as e:
#         logging.error(f"Erro ao criar backup do banco de dados: {e}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def requisitar_dados(url):
    """Faz a requisição para a API com retries automáticos em caso de falha."""
    logging.info(f"Fazendo requisição à API: {url}")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()

def validar_dados(dados):
    """Valida os dados recebidos da API para garantir que são válidos antes da inserção."""
    if dados['temperatura'] is None or dados['precipitacao'] < 0 or dados['umidade'] is None:
        logging.warning("Dados inválidos detectados e ignorados.")
        return False
    return True

def verificar_duplicata(cursor, data):
    """Verifica se um registro com a mesma data já existe no banco de dados."""
    cursor.execute("SELECT COUNT(*) FROM dados_climaticos WHERE data = %s", (data,))
    resultado = cursor.fetchone()
    return resultado[0] > 0

def coletar_dados_previsao(api_key, latitude, longitude):
    """Coleta dados de previsão horária da API One Call."""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    return requisitar_dados(url)

def inserir_dados_no_banco(cursor, data, temperatura, precipitacao, umidade):
    """Insere dados validados no banco de dados MySQL."""
    cursor.execute('''
    INSERT INTO dados_climaticos (data, temperatura, precipitacao, umidade)
    VALUES (%s, %s, %s, %s)
    ''', (data, temperatura, precipitacao, umidade))
    logging.info(f"Dados inseridos: data={data}, temperatura={temperatura}, precipitacao={precipitacao}, umidade={umidade}")

def coletar_e_inserir_dados(api_key, latitude, longitude):
    """Coleta e insere dados de previsão no banco de dados."""
    criar_backup()  
    conn = None  
    try:
        
        password = os.getenv('MYSQL_PASSWORD')
        if not password:
            raise ValueError("A variável de ambiente MYSQL_PASSWORD não está definida.")
        
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,
            database="dados_meteorologicos"
        )
        cursor = conn.cursor()

        ############Coletar dados de previsão##############

        dados_previsao = coletar_dados_previsao(api_key, latitude, longitude)
        if 'list' in dados_previsao:
            for item in dados_previsao['list']:
                data = datetime.datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d %H:%M:%S')
                temperatura = item['main']['temp']
                precipitacao = item.get('rain', {}).get('3h', 0)
                umidade = item['main']['humidity']

                if validar_dados({'data': data, 'temperatura': temperatura, 'precipitacao': precipitacao, 'umidade': umidade}) and not verificar_duplicata(cursor, data):
                    inserir_dados_no_banco(cursor, data, temperatura, precipitacao, umidade)

        conn.commit()
        logging.info("Dados inseridos no banco de dados com sucesso!")
    except mysql.connector.Error as e:
        logging.error(f"Erro ao conectar com o banco de dados MySQL: {e}")
    finally:
        if conn: 
            conn.close()

if __name__ == "__main__":

    if verificar_conexao():

        file_path = 'Local/.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
            api_key = os.getenv("API_KEY")  
            latitude = data['latitude']
            longitude = data['longitude']
            coletar_e_inserir_dados(api_key, latitude, longitude)
    else:
        sys.exit("Conexão com a internet não disponível. Tentando novamente na próxima execução agendada.")