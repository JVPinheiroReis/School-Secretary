# Guia de Contribuição

Obrigado pelo interesse em contribuir com o **School Secretary**! Este documento resume o fluxo de trabalho, padrões de código e requisitos para abrir *Pull Requests*.

Ao participar deste projeto, você concorda em seguir nosso [Código de Conduta](./CODE_OF_CONDUCT.md).

---

## 1. Como Contribuir

- **Reportar Bugs**: Abra uma [Issue](https://github.com/WebCorvus/School-Secretary/issues) utilizando o template de **Bug Report**, detalhando os passos para reproduzir o problema e o comportamento esperado.
- **Sugerir Melhorias**: Abra uma [Issue](https://github.com/WebCorvus/School-Secretary/issues) com o template de **Feature Request**, descrevendo a funcionalidade proposta e seu objetivo.
- **Enviar Código ou Documentação**: Discuta a alteração em uma Issue antes de iniciar a implementação e envie um *Pull Request*.

---

## 2. Configurando o Ambiente

O ambiente completo roda via Docker e é gerenciado pelo script [`controller.sh`](../controller.sh):

```bash
./controller.sh genenvs
./controller.sh start
./controller.sh createsuperuser
```

A aplicação ficará acessível em `http://localhost:8080`. Para instruções detalhadas ou execução fora do Docker, consulte o [Guia de Instalação](../INSTALLATION.md).

---

## 3. Fluxo de Desenvolvimento

### Padrão de Branches e Commits
Crie uma branch a partir de `master` utilizando prefixos semânticos:
- `feat/nome-da-funcionalidade` — Novas funcionalidades.
- `fix/descricao-do-bug` — Correções de erros.
- `docs/atualizacao-doc` — Melhorias na documentação.
- `chore/tarefa-manutencao` — Ajustes de configuração, dependências ou scripts.

### Qualidade e Estilo de Código

#### Backend (`api/`)
- Dependências gerenciadas com **`uv`** em [`api/pyproject.toml`](../api/pyproject.toml).
- Siga a **PEP 8** e as convenções do Django / Django REST Framework.

#### Frontend (`app/`)
- Dependências gerenciadas com **`npm`** em [`app/package.json`](../app/package.json).
- Formatação e lint são feitos com **Biome** e checagem de tipos com **TypeScript**:
  ```bash
  cd app/
  npm run typecheck
  npm run check:write
  ```

### Sincronização entre Backend e Frontend
Sempre que criar ou alterar um endpoint na API Django:
1. Atualize as constantes de rota em [`app/src/config.ts`](../app/src/config.ts).
2. Crie ou ajuste o hook/serviço correspondente em `app/src/hooks/` ou `app/src/services/` utilizando a instância autenticada `api` (`@/services/api`).
3. Atualize a documentação de endpoints em [`api/README.md`](../api/README.md).

---

## 4. Testes Obrigatórios

Toda nova funcionalidade ou correção deve ser acompanhada de testes automatizados. Antes de abrir um Pull Request, execute a suíte completa:

```bash
./controller.sh test
```

Para mais detalhes sobre como criar e rodar testes unitários localmente, consulte o [Guia de Testes](../TESTING.md).

---

## 5. Checklist de Pull Request

Antes de submeter seu PR contra a branch `master`, certifique-se de que:

- [ ] Todos os testes do backend e frontend passam sem erros (`./controller.sh test`).
- [ ] O código do frontend passa na verificação do TypeScript e Biome (`npm run test` em `app/`).
- [ ] A aplicação sobe normalmente com `./controller.sh start`.
- [ ] Novas dependências foram registradas corretamente em `api/pyproject.toml` (`uv.lock`) ou `app/package.json` (`package-lock.json`).
- [ ] A documentação ([`README.md`](../README.md), [`api/README.md`](../api/README.md) ou [`app/README.md`](../app/README.md)) foi atualizada caso haja mudanças em rotas, variáveis de ambiente ou arquitetura.
