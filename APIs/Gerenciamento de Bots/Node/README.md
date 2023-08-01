# API de Gerenciamento de Bots com Node.js

Este é um projeto de API de gerenciamento de bots desenvolvido com Node.js e Express, que permite listar, iniciar, parar e reiniciar bots a partir de um diretório específico. A API também oferece informações sobre o status de execução dos bots.

## Requisitos
- Node.js
- npm (Node Package Manager)

## Instalação
Clone este repositório para o seu computador.

Certifique-se de que o Node.js e npm estejam instalados. Caso não estejam instalados, baixe-os em https://nodejs.org/ e siga as instruções de instalação para o seu sistema operacional.

Instale as dependências do projeto executando o seguinte comando no diretório raiz do projeto:

```
npm install
```

## Como usar

Navegue para o diretório raiz do projeto onde se encontra o arquivo app.js.

Inicie a aplicação executando o seguinte comando:

```
node app.js
```

A API será executada na URL http://localhost:3000/.

## Endpoints
A API disponibiliza os seguintes endpoints:

- GET /: Página inicial da API com links para os endpoints disponíveis.

- GET /bots: Retorna uma lista de bots disponíveis no diretório bots.

- GET /status: Retorna o status de execução de todos os bots.

- GET /status/:bot_name: Retorna o status de execução de um bot específico.

- PUT /start/:bot_name: Inicia a execução de um bot.

- PUT /stop/:bot_name: Para a execução de um bot em andamento.

- PUT /restart/:bot_name: Reinicia um bot que já está em execução.

- GET /management: Retorna informações de gerenciamento sobre os bots.

- POST /shutdown: Encerra a execução da API.

## Estrutura do Diretório
O diretório bots contém os arquivos dos bots disponíveis para execução. Cada arquivo de bot deve ter a extensão .py e seguir um formato adequado para ser gerenciado pela API.

Necessário instalar as dependências deles também.

## Observações

Para iniciar a execução de um bot, o arquivo do bot deve estar presente no diretório bots.

Durante a execução de um bot, informações sobre o status de execução são registradas em arquivos de log com a extensão .log.

O registro de execução de um bot inclui informações sobre início e fim de execução, duração, status e se a execução foi concluída com sucesso.

A função checkRunningBots é um intervalo que verifica periodicamente o status dos bots em execução e os remove da lista de bots em execução quando a execução é concluída.

Para encerrar a execução da API, utilize o endpoint POST /shutdown.

Esta API está sendo desenvolvida para sustentar um site que vai atuar como frontend para gerenciamento dos bots.

Licença
Este projeto está licenciado sob a licença MIT.

