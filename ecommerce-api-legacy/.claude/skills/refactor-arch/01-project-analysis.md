# Project Analysis — Heurísticas de Detecção

Use este guia na **Fase 1** para identificar stack, arquitetura e domínio do projeto.

---

## 1. Detecção de Linguagem e Framework

| Arquivo / Sinal | Linguagem | Framework |
|---|---|---|
| `requirements.txt` contém `flask` | Python | Flask |
| `requirements.txt` contém `django` | Python | Django |
| `requirements.txt` contém `fastapi` | Python | FastAPI |
| `package.json` contém `"express"` | Node.js | Express |
| `package.json` contém `"fastify"` | Node.js | Fastify |
| `package.json` contém `"koa"` | Node.js | Koa |
| `go.mod` presente | Go | (ver imports) |
| `pom.xml` ou `build.gradle` | Java | Spring/Maven |

**Procedimento:**
1. Ler `requirements.txt` ou `package.json` no raiz do projeto
2. Identificar versão do framework (ex: `Flask==3.1.1`)
3. Listar todas as dependências relevantes

---

## 2. Detecção de Banco de Dados

| Sinal no código | Banco |
|---|---|
| `import sqlite3` | SQLite (raw) |
| `flask_sqlalchemy` | SQLAlchemy + SQLite/Postgres |
| `sqlite3` em `package.json` | SQLite (Node.js) |
| `psycopg2` ou `pg` | PostgreSQL |
| `pymongo` ou `mongoose` | MongoDB |
| `redis` | Redis |
| `db = {}` ou array em memória | In-memory (sem persistência real) |

---

## 3. Mapeamento de Arquitetura Atual

### 3.1 Arquitetura Flat (Monolítica)

**Sinais:**
- Poucos arquivos no raiz (≤5 arquivos `.py` ou `.js`)
- Um arquivo único com >200 linhas misturando rotas + queries + lógica
- Imports circulares ou tudo importado de um único módulo

**Exemplos de nomes comuns:** `app.py`, `server.js`, `main.py`, `index.js`

### 3.2 Arquitetura Layered (com alguma separação)

**Sinais:**
- Diretórios `models/`, `routes/`, `services/`, `controllers/`, `utils/`
- Blueprints Flask (`Blueprint`) ou Routers Express (`express.Router()`)
- Imports separados por camada

### 3.3 Arquitetura MVC Adequada

**Sinais:**
- Models apenas com acesso a dados (sem lógica de negócio)
- Controllers apenas orquestrando (sem queries diretas)
- Routes apenas mapeando URL → controller
- Config separado (sem credenciais hardcoded)
- Entry point limpo (apenas wiring)

---

## 4. Identificação do Domínio

Leia os nomes de tabelas, entidades e rotas para inferir o domínio:

| Entidades encontradas | Domínio provável |
|---|---|
| `produtos`, `pedidos`, `usuarios`, `itens_pedido` | E-commerce |
| `tasks`, `categories`, `users` | Task Manager |
| `courses`, `enrollments`, `payments`, `users` | LMS / E-learning |
| `posts`, `comments`, `users` | Blog / CMS |
| `invoices`, `clients`, `items` | Faturamento |

**Como detectar:** ler nomes de tabelas em `CREATE TABLE`, nomes de classes em `models/`, nomes de rotas em `app.py` / `app.js`.

---

## 5. Contagem de Arquivos Fonte

Contar apenas arquivos de código (`.py`, `.js`, `.ts`) excluindo:
- `node_modules/`
- `__pycache__/`
- Arquivos de teste (`*_test.py`, `*.spec.js`)
- Arquivos de configuração (`.env`, `*.json`, `*.yaml`)

---

## 6. Identificação do Entry Point

| Framework | Entry point típico |
|---|---|
| Flask | `app.py` com `app.run()` |
| Express | `app.js` ou `server.js` com `app.listen()` |
| Django | `manage.py` |
| FastAPI | `main.py` com `uvicorn` |

---

## 7. Output Esperado (Fase 1)

Após a análise, imprimir exatamente neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <lista das principais dependências>
Domain:        <domínio inferido> (<entidades principais>)
Architecture:  <Monolítica / Layered / MVC> — <descrição em 1 linha>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas ou entidades>
================================
```
