# Plano de Execução — refactor-arch

Este documento é um briefing completo para um agente executar a skill `refactor-arch` nos 3 projetos legados.
Leia todo o documento antes de começar. Execute uma parte por vez e aguarde confirmação do usuário antes de avançar.

---

## Contexto

A skill `refactor-arch` já foi criada e está em:
```
code-smells-project/.claude/skills/refactor-arch/
├── SKILL.md
├── 01-project-analysis.md
├── 02-antipatterns-catalog.md
├── 03-audit-report-template.md
├── 04-mvc-guidelines.md
└── 05-refactoring-playbook.md
```

A skill executa 3 fases sequenciais:
- **Fase 1 — Análise:** detecta stack, arquitetura e domínio do projeto
- **Fase 2 — Auditoria:** cruza o código contra catálogo de anti-patterns, gera relatório e **pausa para confirmação `[y/n]`**
- **Fase 3 — Refatoração:** reestrutura para MVC, valida boot e endpoints

O repositório raiz é:
```
/Users/fernandoferreira/workspace/mba-ia-refactor-projects-skill/
├── code-smells-project/       ← Projeto 1 (Python/Flask — E-commerce API)
├── ecommerce-api-legacy/      ← Projeto 2 (Node.js/Express — LMS API)
├── task-manager-api/          ← Projeto 3 (Python/Flask — Task Manager)
└── reports/                   ← Relatórios de auditoria (criar se não existir)
```

---

## Parte 1 — Projeto 1: code-smells-project (Python/Flask)

### Contexto do projeto
- **Stack:** Python + Flask 3.1.1 + SQLite (raw sqlite3, sem ORM)
- **Domínio:** E-commerce API (produtos, pedidos, usuários, itens_pedido)
- **Arquitetura atual:** Flat — 4 arquivos sem separação clara de camadas
- **Arquivos principais:** `app.py`, `controllers.py`, `models.py`, `database.py`

### Problemas conhecidos (da análise manual)
- `models.py` é uma God Class com queries para 4 domínios + lógica de negócio
- SQL Injection por concatenação de string em múltiplos pontos de `models.py`
- `SECRET_KEY` hardcoded em `app.py:7`
- Senhas armazenadas em texto puro
- `debug=True` com `host="0.0.0.0"` em `app.py:88`
- N+1 queries em `models.py:171-201` e `models.py:203-233`
- `database.py` mistura conexão + schema + seed numa única função `get_db()`
- Dados sensíveis (SECRET_KEY, db path) expostos no endpoint `/health`

### Passos de execução

1. **Copiar a skill** (já existe no projeto — não precisa copiar):
   ```
   code-smells-project/.claude/skills/refactor-arch/  ← já existe
   ```

2. **Executar a skill** no diretório do projeto:
   ```bash
   cd /Users/fernandoferreira/workspace/mba-ia-refactor-projects-skill/code-smells-project
   # invocar: /refactor-arch
   ```

3. **Validar Fase 1** — o output deve conter:
   ```
   Language:      Python
   Framework:     Flask 3.1.1
   Domain:        E-commerce API (produtos, pedidos, usuários)
   Architecture:  Monolítica — tudo em 4 arquivos, sem separação clara de camadas
   Source files:  4 files analyzed
   ```

4. **Validar Fase 2** — o relatório deve conter no mínimo:
   - 1 finding CRITICAL (SQL Injection ou credencial hardcoded)
   - 1 finding HIGH (debug mode ou God Class)
   - Total ≥ 5 findings
   - Aguardar confirmação `[y/n]` antes da Fase 3

5. **Salvar relatório:**
   - O relatório é gerado em `code-smells-project/reports/audit-report.md`
   - Copiar também para `reports/audit-project-1.md` no repositório raiz

6. **Confirmar Fase 3** com `y` e validar:
   - Nova estrutura MVC criada em `src/`
   - `python app.py` inicia sem erros
   - Endpoints principais respondem (testar com `curl` ou similar)

7. **Commitar** após validação do usuário:
   ```bash
   git add code-smells-project/ reports/audit-project-1.md
   git commit -m "feat: refactor code-smells-project to MVC + audit report"
   ```

### Checklist Parte 1
- [ ] Fase 1 detecta stack corretamente
- [ ] Fase 2 encontra ≥ 5 findings com ao menos 1 CRITICAL ou HIGH
- [ ] Fase 2 pausa e pede confirmação antes da Fase 3
- [ ] Relatório salvo em `reports/audit-project-1.md`
- [ ] Fase 3 cria estrutura MVC
- [ ] Aplicação inicia sem erros após refatoração
- [ ] Endpoints originais respondem corretamente
- [ ] Commit realizado

---

## Parte 2 — Projeto 2: ecommerce-api-legacy (Node.js/Express)

### Contexto do projeto
- **Stack:** Node.js + Express 4.18.2 + SQLite (in-memory, callback-based)
- **Domínio:** LMS API (cursos, matrículas, pagamentos, usuários)
- **Arquitetura atual:** Monolítica — 1 classe `AppManager` contém tudo
- **Arquivos principais:** `src/app.js`, `src/AppManager.js`, `src/utils.js`

### Problemas conhecidos (da análise manual)
- `AppManager.js` é uma God Class extrema: DB init + routing + checkout + relatório numa classe
- Credenciais hardcoded em `utils.js`: `dbPass`, `paymentGatewayKey`, `smtpUser`
- Senha seed "123" hardcoded em `AppManager.js`
- `badCrypto()` em `utils.js` usa base64 repetido como "hash" de senha
- Callback Hell de 7 níveis em `AppManager.js:28-78`
- Cache global mutável em `utils.js:9`
- Sem tratamento de erros nas callbacks do banco
- Dados do cartão de crédito logados no console

### Passos de execução

1. **Copiar a skill** para dentro do projeto:
   ```bash
   cp -r /Users/fernandoferreira/workspace/mba-ia-refactor-projects-skill/code-smells-project/.claude \
         /Users/fernandoferreira/workspace/mba-ia-refactor-projects-skill/ecommerce-api-legacy/
   ```

2. **Executar a skill** no diretório do projeto:
   ```bash
   cd /Users/fernandoferreira/workspace/mba-ia-refactor-projects-skill/ecommerce-api-legacy
   # invocar: /refactor-arch
   ```

3. **Validar Fase 1** — o output deve conter:
   ```
   Language:      JavaScript (Node.js)
   Framework:     Express 4.18.2
   Domain:        LMS API (cursos, matrículas, pagamentos)
   Architecture:  Monolítica — tudo em AppManager.js
   Source files:  3 files analyzed
   ```

4. **Validar Fase 2** — o relatório deve conter no mínimo:
   - 1 finding CRITICAL (credenciais hardcoded ou hash fraco)
   - 1 finding HIGH (God Class ou Callback Hell)
   - Total ≥ 5 findings

5. **Salvar relatório:**
   - Gerado em `ecommerce-api-legacy/reports/audit-report.md`
   - Copiar também para `reports/audit-project-2.md` no repositório raiz

6. **Confirmar Fase 3** com `y` e validar:
   - God Class decomposta em models + controllers + routes separados
   - Callbacks refatorados para async/await
   - `node src/app.js` inicia sem erros
   - Endpoints respondem corretamente

7. **Commitar** após validação do usuário:
   ```bash
   git add ecommerce-api-legacy/ reports/audit-project-2.md
   git commit -m "feat: refactor ecommerce-api-legacy to MVC + audit report"
   ```

### Checklist Parte 2
- [ ] Skill copiada para `ecommerce-api-legacy/.claude/skills/refactor-arch/`
- [ ] Fase 1 detecta Node.js + Express corretamente
- [ ] Fase 2 encontra ≥ 5 findings com ao menos 1 CRITICAL ou HIGH
- [ ] Fase 2 pausa e pede confirmação antes da Fase 3
- [ ] Relatório salvo em `reports/audit-project-2.md`
- [ ] Fase 3 decompõe AppManager em camadas MVC
- [ ] Aplicação inicia sem erros após refatoração
- [ ] Endpoints originais respondem corretamente
- [ ] Commit realizado

---

## Parte 3 — Projeto 3: task-manager-api (Python/Flask)

### Contexto do projeto
- **Stack:** Python + Flask 3.0.0 + SQLAlchemy + Marshmallow + SQLite
- **Domínio:** Task Manager API (tasks, users, categories)
- **Arquitetura atual:** Layered parcial — tem `models/`, `routes/`, `services/`, `utils/` mas com problemas internos
- **Arquivos principais:** `app.py`, `database.py`, `models/`, `routes/`, `services/notification_service.py`, `utils/helpers.py`

### Atenção: este projeto já tem alguma organização
A Fase 3 deve **melhorar** a arquitetura existente, não reconstruir do zero.
Focar em: segurança (MD5, credenciais), N+1 queries, constantes duplicadas, dados sensíveis na resposta.

### Problemas conhecidos (da análise manual)
- Hash de senha com MD5 sem salt em `models/user.py:29,32`
- `password` incluído no `to_dict()` de User — exposto em toda resposta
- Credenciais de email hardcoded em `services/notification_service.py:9-10`
- `SECRET_KEY` hardcoded em `app.py:13`
- `NotificationService` instanciado mas nunca chamado em lugar algum (dead code)
- Rotas sem autenticação (fake JWT: `'fake-jwt-token-' + str(user.id)`)
- Bare excepts em `routes/task_routes.py:62,236` e outros
- N+1 queries em `routes/task_routes.py` e `routes/report_routes.py`
- Constantes de status e prioridade duplicadas em 3+ arquivos
- `debug=True` com `host='0.0.0.0'` em `app.py:34`

### Passos de execução

1. **Copiar a skill** para dentro do projeto:
   ```bash
   cp -r /Users/fernandoferreira/workspace/mba-ia-refactor-projects-skill/code-smells-project/.claude \
         /Users/fernandoferreira/workspace/mba-ia-refactor-projects-skill/task-manager-api/
   ```

2. **Executar a skill** no diretório do projeto:
   ```bash
   cd /Users/fernandoferreira/workspace/mba-ia-refactor-projects-skill/task-manager-api
   # invocar: /refactor-arch
   ```

3. **Validar Fase 1** — o output deve conter:
   ```
   Language:      Python
   Framework:     Flask 3.0.0
   Domain:        Task Manager API (tasks, users, categories)
   Architecture:  Layered — models/routes/services/utils com problemas internos
   Source files:  N files analyzed
   ```

4. **Validar Fase 2** — o relatório deve conter no mínimo:
   - 1 finding CRITICAL (MD5 ou credenciais hardcoded)
   - findings de MEDIUM (N+1, dados sensíveis na resposta)
   - Total ≥ 5 findings
   - Skill deve identificar problemas **mesmo em projeto parcialmente organizado**

5. **Salvar relatório:**
   - Gerado em `task-manager-api/reports/audit-report.md`
   - Copiar também para `reports/audit-project-3.md` no repositório raiz

6. **Confirmar Fase 3** com `y` e validar:
   - MD5 substituído por hash seguro com salt
   - `password` removido de `to_dict()` e respostas da API
   - Credenciais movidas para variáveis de ambiente
   - Constantes centralizadas em `config/constants.py`
   - N+1 queries corrigidas com JOIN ou eager loading
   - `python app.py` inicia sem erros
   - **Todos os endpoints originais continuam respondendo** (este projeto já funciona — não pode regredir)

7. **Commitar** após validação do usuário:
   ```bash
   git add task-manager-api/ reports/audit-project-3.md
   git commit -m "feat: refactor task-manager-api security + quality + audit report"
   ```

### Checklist Parte 3
- [ ] Skill copiada para `task-manager-api/.claude/skills/refactor-arch/`
- [ ] Fase 1 detecta Python + Flask e arquitetura Layered
- [ ] Fase 2 encontra ≥ 5 findings com ao menos 1 CRITICAL ou HIGH
- [ ] Fase 2 pausa e pede confirmação antes da Fase 3
- [ ] Relatório salvo em `reports/audit-project-3.md`
- [ ] MD5 substituído por hash seguro
- [ ] `password` removido das respostas da API
- [ ] Credenciais movidas para `.env`
- [ ] Aplicação inicia sem erros após refatoração
- [ ] Todos os endpoints originais respondem corretamente
- [ ] Commit realizado

---

## Notas para o agente executor

- **Nunca pule a confirmação `[y/n]`** da Fase 2 — é obrigatória pelo exercício
- **Nunca avance para a próxima parte** sem o usuário confirmar que a atual está ok e commitada
- Se a skill não encontrar ≥ 5 findings, ajuste os arquivos de referência em `.claude/skills/refactor-arch/` e execute novamente — é esperado precisar de 2-4 iterações
- O projeto 3 já tem estrutura parcial — a Fase 3 deve melhorar, não reconstruir; priorize segurança sobre reorganização estrutural
- Após cada parte, mostre ao usuário o diff das mudanças antes de commitar
