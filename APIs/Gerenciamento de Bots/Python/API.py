import os
import subprocess
from flask import Flask, jsonify, Response, request
from datetime import datetime, timedelta
import time
import threading
import signal
import sys
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
bots_directory = os.path.join(os.getcwd(), 'bots')


@app.route('/')
def index():
    return '''
    <h1>API de Gerenciamento de Bots</h1>
    <ul>
        <li><a href="/bots">Listar Bots</a></li>
        <li><a href="/status">Status dos Bots</a></li>
        <li><a href="/status/<bot_name>">Status de um Bot</a></li>
        <li><a href="/start/<bot_name>">Iniciar um Bot</a></li>
        <li><a href="/stop/<bot_name>">Parar um Bot</a></li>
        <li><a href="/restart/<bot_name>">Reiniciar um Bot</a></li>
        <li><a href="/management">Gerenciamento de Bots</a></li>
    </ul>
    '''


@app.route('/bots')
def list_bots():
    bots = []

    for filename in os.listdir(bots_directory):
        if filename.endswith('.py'):
            bot_name = filename[:-3]
            bots.append(bot_name)

    return jsonify(bots)


@app.route('/status')
def get_bots_status():
    bots_status = []

    for filename in os.listdir(bots_directory):
        if filename.endswith('.log'):
            bot_name = filename[:-4]
            bot_status = get_bot_status(bot_name)
            if isinstance(bot_status, Response):
                bot_status = bot_status.get_json()
            bot_status['name'] = bot_name
            bot_status['running'] = is_bot_running(bot_name)
            bots_status.append(bot_status)

    return jsonify({'bots_status': bots_status})


@app.route('/status/<bot_name>')
def get_bot_status(bot_name):
    log_file = bot_name + '.log'
    log_path = os.path.join(bots_directory, log_file)

    if not os.path.isfile(log_path):
        return jsonify({'error': 'Bot não encontrado'})

    with open(log_path, 'r') as file:
        lines = file.readlines()

        if len(lines) == 0:
            return jsonify({'error': 'Registro de execução não encontrado'})

        last_execution = lines[-1].strip().split(' | ')

        if len(last_execution) != 7:
            return jsonify({'error': 'Registro de execução inválido'})

        startdate_str = last_execution[0].split(':')[1].strip()
        starttime_parts = last_execution[1].split(':')[1:]
        starttime_str = ':'.join(starttime_parts).strip()
        enddate_str = last_execution[2].split(':')[1].strip()
        endtime_parts = last_execution[3].split(':')[1:]
        endtime_str = ':'.join(endtime_parts).strip()
        duration_parts = last_execution[4].split(':')[1:]
        duration_str = ':'.join(duration_parts).strip()
        completed_str = last_execution[5].split(':')[1].strip()
        status_str = last_execution[6].split(':')[1].strip()

        iniciohora = starttime_str.replace('Início hora da execução: ', '')
        iniciodata = startdate_str.replace('Início data da execução: ', '')
        fimdata = enddate_str.replace('Fim data da execução: ', '')
        fimhora = endtime_str.replace('Fim hora da execução: ', '')
        completed = completed_str.replace('Concluído: ', '')
        status = status_str.replace('Status: ', '')
        duration = duration_str.replace('Tempo de execução: ', '')

        try:
            last_execution_info = {
                'inicio_data_execucao': iniciodata,
                'inicio_hora_execucao': iniciohora,
                'fim_data_execucao': fimdata,
                'fim_hora_execucao': fimhora,
                'tempo_execucao': duration,
                'concluido': 'Sim' if completed == 'True' else 'Erro',
                'status': status,
                'running': is_bot_running(bot_name)
            }

            return jsonify(last_execution_info)

        except ValueError:
            return jsonify({'error': 'Formato inválido de data e hora'})


@app.route('/start/<bot_name>', methods=['PUT'])
def start_bot(bot_name):
    bot_file = bot_name + '.py'
    bot_path = os.path.join(bots_directory, bot_file)

    if not os.path.isfile(bot_path):
        return jsonify({'error': 'Bot não encontrado'})

    if is_bot_running(bot_name):
        return jsonify({'error': 'O bot já está em execução'})

    try:
        process = subprocess.Popen(['python', bot_file], cwd=bots_directory)
        bots_running[bot_name] = process
        return jsonify({'message': 'Bot iniciado com sucesso'})
    except Exception as e:
        return jsonify({'error': 'Erro ao iniciar o bot', 'message': str(e)})


@app.route('/stop/<bot_name>', methods=['PUT'])
def stop_bot(bot_name):
    if not is_bot_running(bot_name):
        return jsonify({'error': 'O bot não está em execução'})

    process = bots_running[bot_name]
    process.kill()
    process.communicate()
    del bots_running[bot_name]

    return jsonify({'message': 'Bot parado com sucesso'})


@app.route('/restart/<bot_name>', methods=['PUT'])
def restart_bot(bot_name):
    stop_bot(bot_name)
    start_bot(bot_name)
    return jsonify({'message': 'Bot reiniciado com sucesso'})


@app.route('/management')
def get_bots_management():
    bots_management = []

    for filename in os.listdir(bots_directory):
        if filename.endswith('.log'):
            bot_name = filename[:-4]
            bot_status = get_bot_status(bot_name)
            if isinstance(bot_status, Response):
                bot_status = bot_status.get_json()
            bot_status['name'] = bot_name
            bots_management.append(bot_status)

    return jsonify({'bots_management': bots_management})


def is_bot_running(bot_name):
    return bot_name in bots_running


def check_running_bots():
    while True:
        bots_to_remove = []
        for bot_name, process in bots_running.items():
            if process.poll() is not None:  # Verifica se o processo terminou
                bots_to_remove.append(bot_name)

        for bot_name in bots_to_remove:
            del bots_running[bot_name]

        # Define o intervalo de verificação dos bots em segundos
        interval = 10
        time.sleep(interval)


def stop_bot_check_thread(signal, frame):
    bot_check_thread.join()  # Aguarda a finalização do bot_check_thread
    sys.exit(0)


@app.route('/shutdown', methods=['POST'])
def shutdown():
    os._exit(0)


if __name__ == '__main__':
    bots_running = {}

    bot_check_thread = threading.Thread(target=check_running_bots)
    bot_check_thread.start()

    # Configura o tratamento de sinal para parar o bot_check_thread
    signal.signal(signal.SIGINT, stop_bot_check_thread)
    signal.signal(signal.SIGTERM, stop_bot_check_thread)

    app.run()
