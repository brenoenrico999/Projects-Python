import requests
import os
import datetime
import time

# Função para verificar o status de um servidor


def verificar_status_servidor(servidor):
    time.sleep(60)

    try:
        response = requests.get(servidor)
        if response.status_code == 200:
            return 'Online'
        else:
            return 'Offline'
    except:
        return 'Erro de conexão'


# Defina o servidor que deseja monitorar
servidor = 'https://www.google.com'

# Registro do início da execução
inicio_execucao = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

# Verificar o status do servidor
status = verificar_status_servidor(servidor)

# Registro do fim da execução
fim_execucao = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

# Cálculo do tempo de execução
inicio_execucao_datetime = datetime.datetime.strptime(
    inicio_execucao, "%Y-%m-%dT%H:%M:%SZ")
fim_execucao_datetime = datetime.datetime.strptime(
    fim_execucao, "%Y-%m-%dT%H:%M:%SZ")
tempo_execucao = str(fim_execucao_datetime - inicio_execucao_datetime)

# Verificar se a execução foi concluída ou se houve erro
concluido = True if status != 'Erro de conexão' else False

# Criar o log com as informações
inicio_data_execucao, inicio_hora_execucao = inicio_execucao.split('T')
fim_data_execucao, fim_hora_execucao = fim_execucao.split('T')

log = f"Início data da execução: {inicio_data_execucao} | Início hora da execução: {inicio_hora_execucao[:-1]} | Fim data da execução: {fim_data_execucao} | Fim hora da execução: {fim_hora_execucao[:-1]} | Tempo de execução: {tempo_execucao} | Concluído: {concluido} | Status: {status}"

# Obter o diretório atual do código
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# Salvar o log em um arquivo na pasta atual
log_file = os.path.join(diretorio_atual, 'monitoramento.log')
with open(log_file, 'a', encoding='utf-8') as file:
    file.write(log + '\n')
