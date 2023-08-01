import random
import datetime
import os
import time
# Função para obter a temperatura atual
def obter_temperatura():
    time.sleep(60)
    # Simulação de obtenção de temperatura
    temperatura = random.uniform(20, 30)
    return round(temperatura, 2)

# Registro do início da execução
inicio_execucao = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

# Obter a temperatura atual
temperatura_atual = obter_temperatura()

# Registro do fim da execução
fim_execucao = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

# Cálculo do tempo de execução
inicio_execucao_datetime = datetime.datetime.strptime(
    inicio_execucao, "%Y-%m-%dT%H:%M:%SZ")
fim_execucao_datetime = datetime.datetime.strptime(
    fim_execucao, "%Y-%m-%dT%H:%M:%SZ")
tempo_execucao = str(fim_execucao_datetime - inicio_execucao_datetime)

# Verificar se a execução foi concluída ou se houve erro
concluido = True

# Criar o log com as informações
inicio_data_execucao, inicio_hora_execucao = inicio_execucao.split('T')
fim_data_execucao, fim_hora_execucao = fim_execucao.split('T')

log = f"Início data da execução: {inicio_data_execucao} | Início hora da execução: {inicio_hora_execucao[:-1]} | Fim data da execução: {fim_data_execucao} | Fim hora da execução: {fim_hora_execucao[:-1]} | Tempo de execução: {tempo_execucao} | Concluído: {concluido} | Temperatura atual: {temperatura_atual}°C"

# Obter o diretório atual do código
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# Salvar o log em um arquivo na pasta atual
log_file = os.path.join(diretorio_atual, 'coleta_temperatura.log')
with open(log_file, 'a', encoding='utf-8') as file:
    file.write(log + '\n')
