# School Secretary

Sistema fullstack de gestão escolar e secretaria acadêmica. Centraliza o controle de alunos, matrículas, turmas, notas, frequência, planejamento de aulas, eventos, acervo/empréstimos de recursos e emissão de documentos em PDF.

---

## Principais Funcionalidades

- **Gestão Acadêmica**: Controle de alunos, responsáveis, matrículas, turmas, disciplinas, itinerários formativos e horários de aulas.
- **Diário do Professor**: Lançamento de notas, registro de presença, planejamento semanal de aulas e reserva de salas.
- **Financeiro e Secretaria**: Gestão de contratos, controle de mensalidades, histórico de pagamentos, advertências e suspensões.
- **Relatórios em PDF**: Emissão automatizada de boletins, relatórios de frequência, histórico acadêmico, relatórios financeiros e contratos.
- **Comunicação e Recursos**: Mural de eventos, agenda escolar, sistema de notificações e controle de empréstimo de materiais/equipamentos.

---

## Arquitetura e Tecnologias

A aplicação é dividida em quatro serviços orquestrados via **Docker Compose**:

| Serviço | Diretório | Tecnologias Principais | Responsabilidade |
| :--- | :--- | :--- | :--- |
| **Proxy** | `proxy/` | Nginx | Ponto de entrada (`:8080`). Roteia `/api/` para o backend e `/` para o frontend. |
| **Frontend** | `app/` | Next.js 15, React 18, TypeScript, Tailwind CSS 4 | Interface do usuário, gerenciamento de sessão via cookies e rotas de autenticação. |
| **Backend** | `api/` | Django 5, DRF, SimpleJWT, Gunicorn, WeasyPrint, `uv` | API RESTful, regras de negócio, autenticação JWT, permissões (RBAC) e geração de PDFs. |
| **Database** | `db/` | PostgreSQL | Persistência relacional dos dados do sistema. |

### Estrutura de Diretórios

```text
School-Secretary/
├── api/                # Backend (Django + Django REST Framework)
│   ├── resources/      # App de recursos escolares e empréstimos
│   ├── school/         # App de turmas, matérias, aulas, salas e eventos
│   ├── students/       # App de alunos, notas, presença, contratos e financeiro
│   ├── users/          # App de autenticação e gerenciamento de usuários
│   └── utils/          # Utilitários (geração de PDFs, relatórios, validações)
├── app/                # Frontend (Next.js App Router)
├── db/                 # Configuração e imagem do PostgreSQL
├── docs/               # Documentos de escopo e requisitos do projeto
├── proxy/              # Configuração do proxy reverso (Nginx)
├── scripts/            # Scripts auxiliares de automação
├── compose.yaml        # Orquestração dos containers de produção/desenvolvimento
├── compose.test.yaml   # Orquestração isolada para execução de testes
└── controller.sh       # CLI para gerenciar o ciclo de vida do projeto
```

---

## Como Executar

### Via Docker (Recomendado)

**Pré-requisitos:** Docker e Docker Compose instalados.

1. **Gere os arquivos `.env` padrão** para todos os serviços:
   ```bash
   ./controller.sh genenvs
   ```

2. **Inicie os containers:**
   ```bash
   ./controller.sh start
   ```

3. **Crie um superusuário (administrador):**
   ```bash
   ./controller.sh createsuperuser
   ```

A aplicação estará disponível em **`http://localhost:8080`**.

#### Outros comandos úteis do `controller.sh`
- `./controller.sh stop` — Encerra os containers em execução.
- `./controller.sh restart` — Reinicia todos os serviços.
- `./controller.sh test` — Executa a suíte completa de testes (backend e frontend) em containers isolados.

> Para instruções de execução manual (sem Docker), consulte o [Guia de Instalação](./INSTALLATION.md).

---

## Autenticação e Controle de Acesso (RBAC)

### Fluxo de Autenticação
1. O usuário realiza login no frontend (`/auth/login`), que solicita um par de tokens JWT (`access` e `refresh`) ao endpoint `POST /api/users/token/`.
2. Os tokens são armazenados em cookies gerenciados pelas rotas internas do Next.js (`/auth/login`, `/auth/refresh`, `/auth/logout`).
3. O `middleware.ts` do Next.js protege as rotas privadas no cliente, enquanto uma instância centralizada do Axios (`app/src/services/api.ts`) injeta automaticamente o cabeçalho `Authorization: Bearer <token>` e renova tokens expirados.

### Níveis de Permissão
O acesso aos endpoints da API e às telas do sistema é controlado pelo papel (`role`) atribuído ao usuário:

- **`STUDENT` (Aluno)**: Visualiza dados acadêmicos próprios, eventos, agenda e notificações.
- **`GUARDIAN` (Responsável)**: Possui visibilidade equivalente à do aluno vinculado, além de acesso a informações contratuais/financeiras.
- **`PROFESSOR` (Professor)**: Gerencia notas, frequência, planejamentos semanais, agenda e reservas de sala de suas turmas.
- **`STAFF` (Secretaria/Administração)**: Acesso administrativo amplo sobre cadastros escolares, matrículas, contratos, recursos e relatórios (não pode criar outros usuários `STAFF`).
- **`SUPERUSER` (Administrador Geral)**: Acesso irrestrito a todo o sistema.

---

## Documentação Complementar

- [**Guia de Instalação (`INSTALLATION.md`)**](./INSTALLATION.md) — Passo a passo para execução com Docker ou localmente.
- [**Guia de Testes (`TESTING.md`)**](./TESTING.md) — Como rodar e criar testes no backend (`manage.py test`) e frontend (`Vitest` + `Biome`).
- [**Documentação da API (`api/README.md`)**](./api/README.md) — Lista detalhada de todos os endpoints REST, parâmetros e exemplos de requisição.
- [**Documentação do Frontend (`app/README.md`)**](./app/README.md) — Mapa de páginas e rotas internas da aplicação Next.js.

---

## Autores

- **João Victor Pinheiro Reis** — Frontend e Sistema de Autenticação
- **João Miguel Freire de Oliveira Mendes** — Backend e Sistema de Logs
