# Catálogo de Anti-Patterns

Use este catálogo na **Fase 2** para cruzar o código do projeto contra os padrões abaixo.
Para cada anti-pattern encontrado, registre arquivo e linhas exatos.

---

## Escala de Severidade

| Severidade | Critério |
|---|---|
| **CRITICAL** | Falha grave de segurança ou arquitetura que expõe dados sensíveis ou impede funcionamento correto |
| **HIGH** | Violação forte de MVC/SOLID que dificulta muito manutenção e testes |
| **MEDIUM** | Problema de performance moderada, padronização ou duplicação de código |
| **LOW** | Legibilidade, nomenclatura ruim, magic numbers |

---

## Anti-Patterns

### AP-01 — SQL Injection via Concatenação de String
**Severidade:** CRITICAL

**Sinais de detecção:**
- `"SELECT … " + str(var)` ou `"SELECT … " + var`
- f-string com variável diretamente em query SQL: `f"SELECT * FROM users WHERE id = {id}"`
- `"… WHERE nome LIKE '%" + termo + "%'"`
- `execute("INSERT INTO … VALUES ('" + nome + "', '" + email + "')")`

**Impacto:** Atacante pode ler, modificar ou deletar qualquer dado do banco. Em SQLite com múltiplos statements, pode destruir toda a base.

**Recomendação:** Usar queries parametrizadas com `?` (SQLite) ou `%s` (PostgreSQL). Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-01).

---

### AP-02 — Credenciais Hardcoded
**Severidade:** CRITICAL

**Sinais de detecção:**
- `SECRET_KEY = "minha-chave-..."` em código-fonte
- `password = "123"` ou `apiKey = "pk_live_..."` literais em arquivo `.py` ou `.js`
- `dbPass: "senha_super_secreta_prod_123"` em objeto de configuração
- `smtpUser` / `smtpPassword` em código-fonte
- `paymentGatewayKey = "pk_live_..."` em arquivo commitado

**Impacto:** Qualquer pessoa com acesso ao repositório tem acesso a sistemas de produção, banco de dados e gateways de pagamento.

**Recomendação:** Mover para variáveis de ambiente via `.env` + `python-dotenv` ou `process.env`. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-02).

---

### AP-03 — Senha em Texto Puro ou Hash Fraco
**Severidade:** CRITICAL

**Sinais de detecção:**
- Senha armazenada como string sem hash: `INSERT INTO usuarios … senha = '` + senha + `'`
- Hash com MD5: `hashlib.md5(pwd.encode()).hexdigest()`
- "Hash" com base64 repetido: `btoa(btoa(btoa(...)))` ou loop de base64
- Comparação direta de senha: `if user['senha'] == senha:`
- Ausência de salt na função de hash

**Impacto:** Banco comprometido expõe todas as senhas. MD5 e base64 são reversíveis em segundos com rainbow tables.

**Recomendação:** Usar `bcrypt` ou `hashlib.sha256` com salt aleatório. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-03).

---

### AP-04 — God Class / God Module
**Severidade:** HIGH

**Sinais de detecção:**
- Arquivo único com >200 linhas contendo: queries SQL + lógica de negócio + roteamento + validação
- Classe única com métodos para múltiplos domínios (ex: `AppManager` com checkout + relatório + deleção de usuário)
- Módulo `models.py` com funções para 4+ entidades diferentes no mesmo arquivo
- Arquivo que importa DB, define rotas E contém regras de negócio

**Impacto:** Impossível testar em isolamento. Qualquer mudança pode quebrar partes não relacionadas.

**Recomendação:** Separar em arquivos por domínio/entidade. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-04).

---

### AP-05 — Lógica de Negócio no Controller ou Route Handler
**Severidade:** HIGH

**Sinais de detecção:**
- Queries SQL ou chamadas ao banco diretamente dentro de função de rota (`@app.route`, `app.get`, `router.post`)
- Cálculos de negócio (desconto, status, validação complexa) dentro do handler
- Handler com >30 linhas de lógica
- Múltiplos `if/else` de regras de negócio dentro do controller

**Impacto:** Lógica de negócio acoplada ao transporte HTTP. Impossível reusar em outros contextos (CLI, testes, workers).

**Recomendação:** Extrair lógica para Model ou Service. Controller apenas orquestra. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-05).

---

### AP-06 — Debug Mode em Produção
**Severidade:** HIGH

**Sinais de detecção:**
- `app.run(debug=True)` em Flask
- `app.config["DEBUG"] = True` sem verificação de ambiente
- `app.run(host="0.0.0.0", port=5000, debug=True)` — expõe debugger interativo na rede
- `NODE_ENV` não verificado antes de habilitar logs verbosos

**Impacto:** O debugger interativo do Flask permite execução arbitrária de código no servidor. `host="0.0.0.0"` expõe o debugger para toda a rede.

**Recomendação:** Usar variável de ambiente `DEBUG=true` e ler com `os.getenv`. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-02).

---

### AP-07 — N+1 Query (Query dentro de Loop)
**Severidade:** MEDIUM

**Sinais de detecção:**
- `cursor.execute()` ou `Model.query.filter_by()` dentro de `for` loop
- Loop que busca registros relacionados um por um: `for pedido in pedidos: buscar_itens(pedido.id)`
- Callbacks aninhados em Node.js que executam queries em sequência para cada item de uma lista
- `db.all()` seguido de loop com `db.get()` para cada item

**Impacto:** N pedidos = N+1 queries ao banco. Com 1000 pedidos, são 1001 queries onde poderia ser 1 JOIN.

**Recomendação:** Usar JOIN ou eager loading. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-06).

---

### AP-08 — Dados Sensíveis Expostos na Resposta da API
**Severidade:** MEDIUM

**Sinais de detecção:**
- `to_dict()` ou serialização que inclui campo `password`, `senha`, `secret_key`, `token`
- Endpoint de health check retornando `SECRET_KEY` ou path do banco
- Resposta de login incluindo hash da senha do usuário
- `JSON.stringify(user)` sem filtrar campos sensíveis

**Impacto:** Qualquer consumidor da API (ou log de resposta) tem acesso a dados que não deveria.

**Recomendação:** Serializar apenas campos explícitos, excluindo sempre `password`/`senha`. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-08).

---

### AP-09 — Callback Hell / Pyramid of Doom
**Severidade:** MEDIUM

**Sinais de detecção (Node.js):**
- Callbacks aninhados em mais de 3 níveis: `db.run(..., () => { db.run(..., () => { db.run(...) }) })`
- Indentação crescendo para a direita com cada operação assíncrona
- Variáveis de controle de fluxo (`pending`, `counter`) para sincronizar callbacks paralelos

**Impacto:** Código impossível de debugar, ordem de execução imprevisível, race conditions silenciosas.

**Recomendação:** Refatorar para `async/await` com `Promise`. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-07).

---

### AP-10 — API Deprecated
**Severidade:** MEDIUM

**Sinais de detecção:**
- `flask.ext.*` — extensões no namespace `ext` foram removidas no Flask 1.0
- `db.session.remove()` chamado em contexto diferente de teardown
- `request.form` sem proteção CSRF em rotas que modificam estado
- Express 3.x APIs (`app.configure`, `app.router`) em projetos com Express 4+
- `sqlite3` callback-based em projeto Node.js moderno (prefira `better-sqlite3` ou versão com promises)
- `md5` de `hashlib` para hashing de senhas (obsoleto para segurança desde 2004)

**Impacto:** Pode causar erros silenciosos em versões mais novas, vulnerabilidades de segurança conhecidas, ou incompatibilidade futura.

**Recomendação:** Atualizar para a API moderna equivalente documentada no framework/biblioteca.

---

### AP-11 — Bare Except / Swallow de Exceção
**Severidade:** LOW

**Sinais de detecção:**
- `except:` sem especificar o tipo de exceção (Python)
- `except Exception as e: pass` sem log
- `except Exception as e: print(e)` sem relançar ou retornar erro estruturado
- Callback `(err, result) => { if (err) return; ... }` sem tratar o erro

**Impacto:** Erros silenciosos impossíveis de diagnosticar em produção. Esconde bugs reais.

**Recomendação:** Capturar exceções específicas e logar com contexto. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-09).

---

### AP-12 — Magic Numbers e Constantes Espalhadas
**Severidade:** LOW

**Sinais de detecção:**
- Mesma lista de valores (`["pendente", "em_andamento", "concluido"]`) repetida em 3+ arquivos
- Número literal sem nome: `if prioridade > 5:` sem constante nomeada
- Validações de range repetidas em model, route e helper
- Categorias hardcoded dentro de função de validação

**Impacto:** Mudança em uma regra exige localizar e alterar todos os arquivos. Fácil de esquecer um.

**Recomendação:** Centralizar em módulo `config/constants.py` ou `config/settings.py`. Ver [05-refactoring-playbook.md](05-refactoring-playbook.md#pb-10).
