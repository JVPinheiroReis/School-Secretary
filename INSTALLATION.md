# Guia de Instalação e Execução

Instruções para configurar e executar o **School Secretary** via Docker (recomendado) ou manualmente no ambiente local.

---

## 1. Execução com Docker (Recomendado)

### Pré-requisitos
- **Docker** e **Docker Compose** instalados.
- **Bash** (Linux/macOS ou Git Bash/WSL no Windows).

### Passo a Passo

1. **Gere os arquivos de variáveis de ambiente (`.env`)**:
   ```bash
   ./controller.sh genenvs
   ```
   > Isso copia os arquivos `.env.example` para `.env` dentro de `api/`, `app/`, `db/` e `proxy/`. Em ambientes de produção, revise e altere as credenciais geradas.

2. **Construa e inicie os containers**:
   ```bash
   ./controller.sh start
   ```
   > O script compila as imagens e aguarda todos os serviços (`db`, `api`, `app` e `proxy`) passarem nos *healthchecks*.

3. **Crie uma conta de superusuário**:
   ```bash
   ./controller.sh createsuperuser
   ```

4. **Acesse a aplicação**:
   - **Aplicação Web (Frontend)**: [`http://localhost:8080`](http://localhost:8080)
   - **Painel Administrativo (Django Admin)**: [`http://localhost:8080/api/admin/`](http://localhost:8080/api/admin/)
   - **API Base**: [`http://localhost:8080/api/`](http://localhost:8080/api/)

### Comandos do `controller.sh`

O script [`controller.sh`](./controller.sh) centraliza as rotinas da pasta [`scripts/`](./scripts/). Adicione a flag `--no-confirm` ao final de qualquer comando para pular a confirmação de encerramento (útil em pipelines CI/CD).

| Comando | Descrição |
| :--- | :--- |
| `./controller.sh genenvs` | Cria os arquivos `.env` a partir dos `.env.example` de cada serviço. |
| `./controller.sh start` | Faz o build das imagens e sobe os containers em background (`docker compose up -d --wait`). |
| `./controller.sh stop` | Para e remove os containers em execução (`docker compose down`). |
| `./controller.sh restart` | Executa `stop` seguido de `start`. |
| `./controller.sh createsuperuser` | Cria um usuário administrador interativamente no container da API. |
| `./controller.sh test` | Sobe um ambiente isolado (`compose.test.yaml`), executa os testes e remove os containers. |
| `./controller.sh publish` | Faz o build e publica as imagens Docker no Docker Hub (`webcorvus/*`). |

---

## 2. Execução Manual (Desenvolvimento Local)

Caso deseje rodar o Backend e o Frontend fora do Docker para desenvolvimento direto:

### Pré-requisitos
- **Python 3.13+** e gerenciador de pacotes [**uv**](https://docs.astral.sh/uv/)
- **Node.js 20+** e **npm**
- **PostgreSQL** em execução local (ou ajuste o `.env` da API para apontar para a instância desejada)

### Configurando o Backend (`api/`)

1. Acesse a pasta da API e gere o arquivo `.env`:
   ```bash
   cd api/
   cp .env.example .env
   ```
   > **Importante:** Edite `api/.env` ajustando `DATABASE_HOST=localhost` (e demais credenciais do seu PostgreSQL local) e remova ou comente `SCRIPT_NAME=/api` se não estiver usando o Nginx na frente.

2. Instale as dependências e aplique as migrações:
   ```bash
   uv sync
   uv run python manage.py makemigrations
   uv run python manage.py migrate
   ```

3. Crie um superusuário e inicie o servidor de desenvolvimento:
   ```bash
   uv run python manage.py createsuperuser
   uv run python manage.py runserver 8000
   ```

### Configurando o Frontend (`app/`)

1. Em outro terminal, acesse a pasta do frontend e gere o arquivo `.env`:
   ```bash
   cd app/
   cp .env.example .env
   ```
   > **Importante:** Caso esteja rodando sem o proxy Nginx, ajuste `NEXT_PUBLIC_PUBLIC_API_HOST=http://localhost:8000/` e `NEXT_PUBLIC_PRIVATE_API_HOST=http://localhost:8000/` no arquivo `app/.env`.

2. Instale as dependências e inicie o servidor Next.js:
   ```bash
   npm install
   npm run dev
   ```

3. Acesse o frontend em [`http://localhost:3000`](http://localhost:3000).

---

## 3. Variáveis de Ambiente

Cada serviço possui seu próprio `.env.example`:

- **[`api/.env.example`](./api/.env.example)**: Configurações do Django (`DJANGO_SECRET_KEY`, `DEBUG`, `DJANGO_ALLOWED_HOSTS`), conexão com o banco (`DATABASE_*`), CORS/CSRF e prefixo de rota (`SCRIPT_NAME=/api`).
- **[`app/.env.example`](./app/.env.example)**: Porta do servidor Node (`PORT=3000`) e URLs públicas/internas da API (`NEXT_PUBLIC_PUBLIC_API_HOST` e `NEXT_PUBLIC_PRIVATE_API_HOST`).
- **[`db/.env.example`](./db/.env.example)**: Credenciais e diretório de dados do PostgreSQL (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `PGPORT`).
