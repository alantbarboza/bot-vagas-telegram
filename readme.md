# Bot de Busca Automatizada de Vagas

## Sobre o projeto

Bot desenvolvido em Python para realizar a busca automatizada de vagas de tecnologia em múltiplos portais de emprego, aplicando filtros personalizados para cada usuário e enviando os resultados diretamente pelo Telegram.

O objetivo do projeto é reduzir o tempo gasto procurando vagas manualmente, centralizando oportunidades relevantes em um único local.

Este projeto foi desenvolvido com foco em automação, web scraping, integração com APIs, programação assíncrona e organização de aplicações Python.


---

## Funcionalidades

* Busca automática de vagas em múltiplos sites.
* Busca manual através de comandos do Telegram.
* Filtros personalizados por usuário.
* Remoção de vagas duplicadas.
* Filtragem por período de publicação.
* Classificação de vagas por pontuação de compatibilidade.
* Envio automático de vagas em horários individuais por usuário.
* Controle de permissões para grupos do Telegram.
* Gerenciamento dinâmico de filtros sem necessidade de alterar o código.

---

## Sites monitorados

Atualmente o bot realiza buscas nos seguintes portais:

* LinkedIn
* Nerdin
* Sólides
* Empregos.com.br
* InfoJobs
* 99Jobs

Cada portal possui um extrator independente para facilitar manutenção e futuras expansões.

---

## Como funciona a extração

1. Cada usuário possui um horário próprio de execução automática configurado no sistema.
2. No horário agendado, o bot realiza a busca utilizando apenas os termos de busca daquele usuário.
3. Realiza buscas nos portais configurados.
4. Coleta informações como:
   * Título da vaga
   * Empresa
   * Localização
   * Data de publicação
   * Link da vaga
5. Remove vagas duplicadas.
6. Filtra vagas fora do período configurado.
7. Avalia cada vaga utilizando os critérios definidos pelo usuário.
8. Ordena os resultados pela pontuação obtida.
9. Envia apenas as vagas compatíveis via Telegram.

**Observação:** O sistema impede execuções simultâneas. Caso uma busca manual (`/vagas`) esteja em andamento, a execução automática será ignorada, e vice-versa.

---

## Sistema de pontuação

Cada vaga recebe pontos de acordo com a compatibilidade com os filtros do usuário:

* Nível profissional
* Cargo
* Tecnologias
* Localização

Vagas contendo palavras bloqueadas são descartadas automaticamente.

---

## Comandos disponíveis

### Busca e monitoramento

* `/vagas` - Executa a busca manual de vagas.
* `/proxima_execucao` - Exibe a próxima execução automática.
* `/online` - Mostra o tempo de atividade do bot.

### Gerenciamento de filtros

* `/filtros` - Exibe os filtros atuais.
* `/add campo valor` - Adiciona filtros.
* `/rem campo valor` - Remove filtros.

Exemplo:

```text
/add tecnologias python
/rem tecnologias java
```

### Utilidades

* `/comandos` - Lista todos os comandos.
* `/meu_id` - Exibe o ID do usuário.
* `/limpar` - Remove mensagens armazenadas pelo bot.

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/alantbarboza/bot-vagas-telegram.git
cd bot-vagas-telegram
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```
 
### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
API_KEY=sua_api_key
PORT=10000
WEBHOOK_URL=https://seu-servico.onrender.com
```

Onde:
* `API_KEY`: chave utilizada para acesso à API utilizada pelo sistema.
* `PORT`: porta usada pelo servidor HTTP.
* `WEBHOOK_URL`: URL pública onde o bot está hospedado (Render, Railway, etc.)

### 4. Execute o projeto

```bash
python main.py
```

---

## Tecnologias utilizadas

* Python
* Aiogram (Telegram Bot Framework)
* aiohttp (Servidor Web / Webhook)
* Playwright (Web Scraping)
* AsyncIO (Programação assíncrona)
* Telegram Bot API

---

## Estrutura do projeto

```text
bot-vagas-telegram/

├── bot/
├── vagas/
├── agendamento/
├── utils/
├── imagens/
└── main.py
```


