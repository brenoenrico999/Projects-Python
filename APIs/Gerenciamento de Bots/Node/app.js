const express = require('express');
const cors = require('cors');
const childProcess = require('child_process');
const fs = require('fs');

const app = express();
const bots_directory = __dirname + '/bots';
const bots_running = {};

app.use(express.json());
app.use(cors());

app.get('/', (req, res) => {
  res.send(`
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
  `);
});

app.get('/bots', (req, res) => {
  const bots = fs
    .readdirSync(bots_directory)
    .filter((filename) => filename.endsWith('.py'))
    .map((filename) => filename.slice(0, -3));
  res.json(bots);
});

app.get('/status', (req, res) => {
  const bots_status = fs
    .readdirSync(bots_directory)
    .filter((filename) => filename.endsWith('.log'))
    .map((filename) => {
      const bot_name = filename.slice(0, -4);
      const bot_status = getBotStatus(bot_name);
      bot_status.name = bot_name;
      bot_status.running = isBotRunning(bot_name);
      return bot_status;
    });
  res.json({ bots_status });
});

app.get('/status/:bot_name', (req, res) => {
  const bot_name = req.params.bot_name;
  const log_file = bot_name + '.log';
  const log_path = bots_directory + '/' + log_file;

  if (!fs.existsSync(log_path)) {
    return res.json({ error: 'Bot não encontrado' });
  }

  const lines = fs.readFileSync(log_path, 'utf8').split('\n');

  if (lines.length === 0) {
    return res.json({ error: 'Registro de execução não encontrado' });
  }

  const last_execution = lines[lines.length - 1].split(' | ');

  if (last_execution.length !== 7) {
    return res.json({ error: 'Registro de execução inválido' });
  }

  const startdate_str = last_execution[0].split(':')[1].trim();
  const starttime_str = last_execution[1].split(':')[1].trim();
  const enddate_str = last_execution[2].split(':')[1].trim();
  const endtime_str = last_execution[3].split(':')[1].trim();
  const duration_str = last_execution[4].split(':')[1].trim();
  const completed_str = last_execution[5].split(':')[1].trim();
  const status_str = last_execution[6].split(':')[1].trim();

  const iniciohora = starttime_str.replace('Início hora da execução: ', '');
  const iniciodata = startdate_str.replace('Início data da execução: ', '');
  const fimdata = enddate_str.replace('Fim data da execução: ', '');
  const fimhora = endtime_str.replace('Fim hora da execução: ', '');
  const completed = completed_str.replace('Concluído: ', '');
  const status = status_str.replace('Status: ', '');
  const duration = duration_str.replace('Tempo de execução: ', '');

  try {
    const last_execution_info = {
      inicio_data_execucao: iniciodata,
      inicio_hora_execucao: iniciohora,
      fim_data_execucao: fimdata,
      fim_hora_execucao: fimhora,
      tempo_execucao: duration,
      concluido: completed === 'True' ? 'Sim' : 'Erro',
      status: status,
      running: isBotRunning(bot_name),
    };

    return res.json(last_execution_info);
  } catch (err) {
    return res.json({ error: 'Formato inválido de data e hora' });
  }
});

app.put('/start/:bot_name', (req, res) => {
  const bot_name = req.params.bot_name;
  const bot_file = bot_name + '.py';
  const bot_path = bots_directory + '/' + bot_file;

  if (!fs.existsSync(bot_path)) {
    return res.json({ error: 'Bot não encontrado' });
  }

  if (isBotRunning(bot_name)) {
    return res.json({ error: 'O bot já está em execução' });
  }

  try {
    const process = childProcess.spawn('python', [bot_file], {
      cwd: bots_directory,
    });
    bots_running[bot_name] = process;
    return res.json({ message: 'Bot iniciado com sucesso' });
  } catch (err) {
    return res.json({ error: 'Erro ao iniciar o bot', message: err.message });
  }
});

app.put('/stop/:bot_name', (req, res) => {
  const bot_name = req.params.bot_name;

  if (!isBotRunning(bot_name)) {
    return res.json({ error: 'O bot não está em execução' });
  }

  const process = bots_running[bot_name];
  process.kill();
  process.on('close', () => {
    delete bots_running[bot_name];
    return res.json({ message: 'Bot parado com sucesso' });
  });
});

app.put('/restart/:bot_name', (req, res) => {
  const bot_name = req.params.bot_name;
  if (!isBotRunning(bot_name)) {
    return res.json({ error: 'O bot não está em execução' });
  }

  const process = bots_running[bot_name];
  process.kill();
  process.on('close', () => {
    delete bots_running[bot_name];
    startBot(bot_name);
    return res.json({ message: 'Bot reiniciado com sucesso' });
  });
});

app.get('/management', (req, res) => {
  const bots_management = fs
    .readdirSync(bots_directory)
    .filter((filename) => filename.endsWith('.log'))
    .map((filename) => {
      const bot_name = filename.slice(0, -4);
      const bot_status = getBotStatus(bot_name);
      bot_status.name = bot_name;
      return bot_status;
    });
  res.json({ bots_management });
});

app.post('/shutdown', (req, res) => {
  process.exit(0);
});

function getBotStatus(bot_name) {
  const log_file = bot_name + '.log';
  const log_path = bots_directory + '/' + log_file;

  if (!fs.existsSync(log_path)) {
    return { error: 'Bot não encontrado' };
  }

  const lines = fs.readFileSync(log_path, 'utf8').split('\n');

  if (lines.length === 0) {
    return { error: 'Registro de execução não encontrado' };
  }

  const last_execution = lines[lines.length - 1].split(' | ');

  if (last_execution.length !== 7) {
    return { error: 'Registro de execução inválido' };
  }

  const startdate_str = last_execution[0].split(':')[1].trim();
  const starttime_str = last_execution[1].split(':')[1].trim();
  const enddate_str = last_execution[2].split(':')[1].trim();
  const endtime_str = last_execution[3].split(':')[1].trim();
  const duration_str = last_execution[4].split(':')[1].trim();
  const completed_str = last_execution[5].split(':')[1].trim();
  const status_str = last_execution[6].split(':')[1].trim();

  const iniciohora = starttime_str.replace('Início hora da execução: ', '');
  const iniciodata = startdate_str.replace('Início data da execução: ', '');
  const fimdata = enddate_str.replace('Fim data da execução: ', '');
  const fimhora = endtime_str.replace('Fim hora da execução: ', '');
  const completed = completed_str.replace('Concluído: ', '');
  const status = status_str.replace('Status: ', '');
  const duration = duration_str.replace('Tempo de execução: ', '');

  try {
    const last_execution_info = {
      inicio_data_execucao: iniciodata,
      inicio_hora_execucao: iniciohora,
      fim_data_execucao: fimdata,
      fim_hora_execucao: fimhora,
      tempo_execucao: duration,
      concluido: completed === 'True' ? 'Sim' : 'Erro',
      status: status,
    };

    return last_execution_info;
  } catch (err) {
    return { error: 'Formato inválido de data e hora' };
  }
}

function isBotRunning(bot_name) {
  return bot_name in bots_running;
}

function checkRunningBots() {
  setInterval(() => {
    Object.keys(bots_running).forEach((bot_name) => {
      const process = bots_running[bot_name];
      if (process.exitCode !== null) {
        delete bots_running[bot_name];
      }
    });
  }, 10000); // Check every 10 seconds
}

checkRunningBots(); // Start the checkRunningBots function

const server = app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});

// Gracefully handle shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down gracefully...');
  server.close(() => {
    console.log('Server closed.');
    process.exit(0);
  });
});
