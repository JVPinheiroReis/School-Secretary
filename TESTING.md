# Guia de Testes e Qualidade de Código

Este documento descreve como executar a suíte de testes, as verificações estáticas e como estruturar novos testes no **School Secretary**.

---

## 1. Executando os Testes

### Via Docker (Recomendado)

Para executar todos os testes (Frontend e Backend) em containers temporários e isolados (definidos em [`compose.test.yaml`](./compose.test.yaml)):

```bash
./controller.sh test

# Para execução sem pausa de confirmação no final (ex.: CI/CD):
./controller.sh test --no-confirm
```

O script [`scripts/test.sh`](./scripts/test.sh) realiza automaticamente:
1. Limpeza de volumes e containers de teste anteriores.
2. Build e inicialização dos serviços de teste aguardando os *healthchecks*.
3. Execução da checagem de tipos, linter e testes unitários do Frontend (`app`).
4. Execução dos testes automatizados do Backend (`api`).
5. Remoção automática dos containers e volumes ao finalizar.

---

### Localmente (Manual)

Certifique-se de ter configurado o ambiente conforme o [Guia de Instalação](./INSTALLATION.md).

#### Backend (`api/`)
Utiliza o framework nativo de testes do Django (`unittest` / `APITestCase`):

```bash
cd api/

# Executar toda a suíte de testes
uv run python manage.py test

# Executar testes de um app específico (users, school, students ou resources)
uv run python manage.py test school
```

#### Frontend (`app/`)
Utiliza **TypeScript** (`tsc`), **Biome** (formatação e lint) e **Vitest** + **Testing Library** (testes de componentes e hooks):

```bash
cd app/

# Executa typecheck + biome check + vitest run
npm run test

# Comandos individuais de qualidade de código:
npm run typecheck     # Verifica tipagem TypeScript (tsc --noEmit)
npm run check         # Analisa formatação e lint com Biome
npm run check:write   # Corrige problemas de formatação e lint automaticamente
```

---

## 2. Estrutura e Criação de Testes

### Backend (`api/`)
Os testes ficam dentro da pasta `tests/` de cada app Django, divididos por responsabilidade:

- `api/{app}/tests/test_models.py` — Regras de negócio, validações e métodos dos models.
- `api/{app}/tests/test_serializers.py` — Validação de payloads e serialização de dados.
- `api/{app}/tests/test_views.py` — Endpoints REST, permissões por papel (RBAC) e ações customizadas.

> **Convenção:** Todo arquivo de teste deve começar com o prefixo `test_` (ex.: `test_views.py`) para ser descoberto automaticamente pelo `manage.py test`.

### Frontend (`app/`)
Os arquivos de teste ficam **colocalizados** junto ao componente, página, contexto ou hook que testam, utilizando o sufixo `.test.ts` ou `.test.tsx`:

- **Componentes**: `app/src/components/UserInfoCard/index.test.tsx`
- **Hooks**: `app/src/hooks/useEvent.test.ts`
- **Contextos**: `app/src/contexts/UserContext.test.tsx`
- **Páginas**: `app/src/app/(account)/dashboard/page.test.tsx`

---

## 3. Logs e Monitoramento de Exceções

O Backend conta com um middleware de captura de exceções ([`api/school/middleware.py`](./api/school/middleware.py)) e configuração de logger em [`api/users/logger.py`](./api/users/logger.py).

Para acompanhar os logs da API em tempo real quando estiver rodando com Docker:

```bash
docker compose logs -f api
```
