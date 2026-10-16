# Documentação da API (Backend)

API RESTful desenvolvida com **Django 5** e **Django REST Framework (DRF)**, responsável pelas regras de negócio, controle de acesso baseado em papéis (RBAC), autenticação JWT e geração de relatórios em PDF.

---

## 1. Visão Geral e Acesso

- **URL Base (via Proxy Docker)**: `http://localhost:8080/api/`
- **Painel Django Admin**: `http://localhost:8080/api/admin/`
- **Autenticação**: Tokens JWT via cabeçalho HTTP:
  ```http
  Authorization: Bearer <access_token>
  ```

### Padrão CRUD dos ViewSets
Todos os recursos listados abaixo utilizam o `ModelViewSet` do DRF e oferecem suporte às operações padrão (respeitando as permissões do usuário):
- `GET /{recurso}/` — Lista registros (suporta paginação e busca com `?search=`).
- `POST /{recurso}/` — Cria um novo registro.
- `GET /{recurso}/{id}/` — Retorna os detalhes de um registro específico.
- `PUT /{recurso}/{id}/` ou `PATCH /{recurso}/{id}/` — Atualiza um registro.
- `DELETE /{recurso}/{id}/` — Remove um registro.

---

## 2. Endpoints por Módulo

### Autenticação e Usuários (`/api/users/`)

| Endpoint | Método(s) | Permissão | Descrição |
| :--- | :--- | :--- | :--- |
| `/api/users/token/` | `POST` | Público | Autentica com `email` e `password`, retornando os tokens `access` e `refresh`. |
| `/api/users/token/refresh/` | `POST` | Público | Renova o token `access` a partir de um `refresh` válido. |
| `/api/users/me/` | `GET` | Autenticado | Retorna os dados completos e o perfil do usuário autenticado. |
| `/api/users/` | CRUD | `STAFF` | Gerenciamento geral de contas de usuários. |

---

### Gestão Escolar (`/api/school/`)

#### Recursos Principais (CRUD)

| Recurso | Endpoint Base | Leitura (`GET`) | Escrita (`POST`/`PUT`/`DELETE`) | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **Professores** | `/api/school/professors/` | `STAFF` | `STAFF` | Cadastro de professores. |
| **Matérias** | `/api/school/subjects/` | Autenticado | `STAFF` | Disciplinas escolares. |
| **Itinerários** | `/api/school/itineraries/` | Autenticado | `STAFF` | Itinerários formativos e grades curriculares. |
| **Turmas** | `/api/school/groups/` | Autenticado | `STAFF` | Turmas e séries escolares. |
| **Aulas** | `/api/school/lessons/` | Autenticado | `STAFF` | Horários e alocação de aulas por turma/professor. |
| **Planejamento Semanal** | `/api/school/weekly-plans/` | Autenticado | `PROFESSOR` | Planejamento semanal de conteúdo e objetivos de aula. |
| **Agenda** | `/api/school/agenda/` | Autenticado | `PROFESSOR` | Atividades, tarefas e lembretes das turmas. |
| **Eventos** | `/api/school/events/` | Autenticado | `STAFF` | Eventos escolares e comunicados gerais. |
| **Inscrições em Eventos** | `/api/school/event-registrations/` | Autenticado | Autenticado | Registro de participação de alunos em eventos. |
| **Salas** | `/api/school/rooms/` | Autenticado | `STAFF` | Salas de aula e laboratórios. |
| **Reservas de Sala** | `/api/school/room-reservations/` | Autenticado | `PROFESSOR` | Agendamento de uso de salas por professores. |
| **Notificações** | `/api/school/notifications/` | Autenticado (próprias) | `STAFF` | Alertas e mensagens direcionadas aos usuários. |
| **Livros** | `/api/school/books/` | Autenticado | `STAFF` | Catálogo de livros didáticos e acervo. |
| **Registros Escolares** | `/api/school/schoolrecords/` | `STAFF` | `STAFF` | Histórico e registros administrativos escolares. |

#### Ações Especiais de `/api/school/`

| Endpoint | Método | Descrição |
| :--- | :--- | :--- |
| `/api/school/groups/{id}/get-lessons/` | `GET` | Grade semanal de aulas de uma turma específica. |
| `/api/school/groups/{id}/performance-report/` | `GET` | Relatório de desempenho acadêmico da turma. |
| `/api/school/groups/{id}/efficiency-analysis/?year=YYYY` | `GET` | Análise de eficiência (taxas de aprovação e evasão) da turma no ano informado. |
| `/api/school/agenda/pendents/` | `GET` | Lista apenas os itens futuros/pendentes da agenda. |
| `/api/school/events/pendents/` | `GET` | Lista apenas os próximos eventos escolares. |
| `/api/school/events/{id}/register/` | `POST` | Inscreve um aluno no evento especificado. |
| `/api/school/notifications/{id}/mark-read/` | `POST` | Marca uma notificação específica como lida. |
| `/api/school/notifications/mark-all-read/` | `POST` | Marca todas as notificações do usuário logado como lidas. |

---

### Alunos, Acadêmico e Financeiro (`/api/students/`)

#### Recursos Principais (CRUD)

| Recurso | Endpoint Base | Leitura (`GET`) | Escrita (`POST`/`PUT`/`DELETE`) | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **Alunos** | `/api/students/` | Autenticado | `STAFF` | Cadastro e dados cadastrais de estudantes. |
| **Notas** | `/api/students/grades/` | Autenticado | `PROFESSOR` | Avaliações e notas por disciplina e bimestre/etapa. |
| **Frequência** | `/api/students/presences/` | Autenticado | `PROFESSOR` | Registro de presença e faltas por aula/data. |
| **Responsáveis** | `/api/students/guardians/` | Autenticado | `STAFF` | Pais ou responsáveis legais vinculados aos alunos. |
| **Matrículas** | `/api/students/enrollments/` | Autenticado | `STAFF` | Vínculo de matrícula do aluno em turmas/anos letivos. |
| **Contratos** | `/api/students/contracts/` | Autenticado | `STAFF` | Contratos de prestação de serviços educacionais. |
| **Mensalidades** | `/api/students/tuitions/` | Autenticado | `STAFF` | Cobranças e controle de pagamento de mensalidades. |
| **Advertências** | `/api/students/warnings/` | Autenticado | `STAFF` | Registros disciplinares de advertência. |
| **Suspensões** | `/api/students/suspensions/` | Autenticado | `STAFF` | Registros disciplinares de suspensão. |

#### Relatórios, PDFs e Ações Especiais de `/api/students/`

| Endpoint | Método | Descrição |
| :--- | :--- | :--- |
| `/api/students/{id}/download-grades/` | `GET` | Gera e baixa o boletim de notas do aluno em **PDF**. |
| `/api/students/{id}/download-presence/` | `GET` | Gera e baixa o relatório de frequência do aluno em **PDF**. |
| `/api/students/{id}/academic-report/` | `GET` | Retorna o relatório acadêmico consolidado do aluno em **JSON**. |
| `/api/students/{id}/download-academic-report/` | `GET` | Gera e baixa o relatório acadêmico completo do aluno em **PDF**. |
| `/api/students/students-needing-attention/` | `GET` | Lista alunos em situação crítica de notas ou faltas. |
| `/api/students/efficiency-analysis/?year=YYYY` | `GET` | Análise global de aprovação e evasão escolar no ano informado. |
| `/api/students/presences/absence-report/` | `GET` | Relatório de alunos com índice de faltas superior a 25%. |
| `/api/students/contracts/{id}/download-contract/` | `GET` | Gera e baixa o contrato educacional em **PDF**. |
| `/api/students/tuitions/payment-history/?student_id={id}` | `GET` | Histórico de pagamentos de mensalidades do aluno. |
| `/api/students/tuitions/financial-report/?student_id={id}` | `GET` | Relatório financeiro do aluno em **JSON**. |
| `/api/students/tuitions/download-financial-report/?student_id={id}` | `GET` | Gera e baixa o relatório financeiro do aluno em **PDF**. |

---

### Recursos e Empréstimos (`/api/resources/`)

| Recurso | Endpoint Base | Leitura (`GET`) | Escrita (`POST`/`PUT`/`DELETE`) | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **Recursos** | `/api/resources/` | Autenticado | `STAFF` | Patrimônio, equipamentos, computadores e materiais escolares. |
| **Empréstimos** | `/api/resources/loans/` | Autenticado | `STAFF` | Controle de retirada e devolução de recursos por alunos. |

---

## 3. Convenções Internas da API

- **Serializers Compactos**: Para evitar importações circulares e payloads excessivos em relacionamentos aninhados, cada `models.py` possui serializers completos (ex.: `GroupSerializer`) e versões compactas (ex.: `GroupCompactSerializer`) em `serializers.py`.
- **Geração de PDFs**: Centralizada em [`api/utils/pdfgen.py`](./utils/pdfgen.py), renderizando templates HTML localizados em [`api/templates/`](./templates/).
- **Parâmetros de Consulta Comuns**:
  - `?search=<termo>` — Filtra resultados nos campos configurados em `search_fields` de cada ViewSet.
  - `?page=<n>` e `?page_size=<n>` — Controle de paginação.
