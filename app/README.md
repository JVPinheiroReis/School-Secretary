# Documentação do Frontend (`app/`)

Interface web construída com **Next.js 15 (App Router)**, **React 18**, **TypeScript**, **Tailwind CSS 4** e componentes **Radix UI**.

---

## 1. Estrutura Interna (`app/src/`)

```text
app/src/
├── app/                # Rotas e páginas do Next.js (App Router)
│   ├── (account)/      # Rotas autenticadas, login e route handlers de sessão
│   ├── (announcements)/ # Mural de avisos, agenda, eventos, aulas e notificações
│   ├── (marketing)/    # Páginas institucionais (/about)
│   └── healthcheck/    # Endpoint de verificação de saúde do container
├── components/         # Componentes visuais reutilizáveis e UI (Radix/Tailwind)
├── contexts/           # Contextos globais React (ex.: UserContext)
├── hooks/              # Custom hooks para consumo de dados da API
├── lib/                # Utilitários de estilização (clsx / tailwind-merge)
├── services/           # Cliente HTTP Axios (api.ts) e serviços de autenticação
├── types/              # Definições de tipos e interfaces TypeScript
├── utils/              # Funções utilitárias (ex.: download de arquivos/PDFs)
├── config.ts           # Centralização das URLs da API e rotas de navegação
└── middleware.ts       # Proteção de rotas privadas e redirecionamento de sessão
```

---

## 2. Páginas da Aplicação

Quando executado via Docker Compose (com Nginx), o frontend responde em `http://localhost:8080/`. Em execução isolada (`npm run dev`), responde em `http://localhost:3000/`.

| Rota | Arquivo Principal | Acesso | Descrição |
| :--- | :--- | :--- | :--- |
| `/` | `app/(account)/page.tsx` | Público | Tela de login do sistema. Redireciona usuários autenticados para `/dashboard`. |
| `/dashboard` | `app/(account)/dashboard/page.tsx` | Privado | Painel principal adaptado ao papel do usuário (`STUDENT`, `GUARDIAN`, `PROFESSOR`, `STAFF`). |
| `/profile` | `app/(account)/profile/page.tsx` | Privado | Visualização dos dados cadastrais e perfil do usuário logado. |
| `/week-planning` | `app/(account)/week-planning/page.tsx` | Privado | Consulta e gerenciamento de planejamentos semanais de aula. |
| `/resources` | `app/(account)/resources/page.tsx` | Privado | Listagem de recursos escolares e controle de empréstimos. |
| `/agenda` | `app/(announcements)/agenda/page.tsx` | Privado | Agenda escolar com tarefas e compromissos das turmas. |
| `/events` | `app/(announcements)/events/page.tsx` | Privado | Mural de eventos escolares e inscrições. |
| `/inbox` | `app/(announcements)/inbox/page.tsx` | Privado | Caixa de entrada de notificações do usuário. |
| `/lessons` | `app/(announcements)/lessons/page.tsx` | Privado | Grade de horários e aulas. |
| `/about` | `app/(marketing)/about/page.tsx` | Público | Página institucional com informações sobre o sistema. |

---

## 3. Route Handlers Internos (Next.js API)

O frontend possui rotas internas de servidor para intermediar a autenticação com o Django e gerenciar cookies de sessão com segurança:

| Rota | Método | Descrição |
| :--- | :--- | :--- |
| `/auth/login` | `POST` | Envia credenciais para a API Django (`/api/users/token/`) e salva os tokens JWT nos cookies. |
| `/auth/refresh` | `POST` | Atualiza o token de acesso expirado utilizando o `refresh` token armazenado em cookie. |
| `/auth/logout` | `POST` | Limpa os cookies de autenticação e encerra a sessão do usuário. |
| `/healthcheck` | `GET` | Retorna `200 OK` para monitoramento de saúde do container Docker. |

---

## 4. Comunicação com a API e Convenções

1. **Configuração Centralizada de Rotas ([`src/config.ts`](./src/config.ts))**:
   - `ROUTES`: URLs públicas da API (usadas em chamadas originadas no navegador, via `/api/...`).
   - `ROUTES_INTERNAL`: URLs privadas da rede interna do Docker (`http://api:8000/api/...`, usadas em chamadas Server-Side/Route Handlers).
   - `NAVIGATION`: Constantes com os caminhos das páginas do frontend e atalhos para o Django Admin.

2. **Cliente HTTP Autenticado ([`src/services/api.ts`](./src/services/api.ts))**:
   - Sempre importe a instância configurada (`import api from "@/services/api"`) em vez do `axios` puro.
   - Os interceptors anexados injetam automaticamente o token JWT (`Authorization: Bearer ...`) e tentam renovar a sessão caso recebam `401 Unauthorized`.

3. **Custom Hooks ([`src/hooks/`](./src/hooks/))**:
   - A busca de dados nas páginas e componentes é encapsulada em hooks dedicados (`useStudent`, `useEvent`, `useAgenda`, `useGroup`, `useProfessor`, `useResource`, `useNotification`, `useWeeklyLessonPlan`, etc.).

---

## 5. Scripts Disponíveis (`package.json`)

Execute a partir do diretório `app/`:

| Comando | Descrição |
| :--- | :--- |
| `npm run dev` | Inicia o servidor de desenvolvimento do Next.js na porta `3000`. |
| `npm run build` | Compila a aplicação para produção. |
| `npm run start` | Inicia o servidor Next.js em modo de produção (após `build`). |
| `npm run test` | Executa checagem de tipos (`tsc`), formatação/lint (`biome`) e testes unitários (`vitest`). |
| `npm run typecheck` | Valida a tipagem TypeScript sem emitir arquivos (`tsc --noEmit`). |
| `npm run check` | Verifica formatação e regras de lint em `src/` com **Biome**. |
| `npm run check:write` | Corrige automaticamente formatação e lint em `src/` com **Biome**. |
