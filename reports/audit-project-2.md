================================
PHASE 1: PROJECT ANALYSIS — ecommerce-api-legacy
================================
Language:      JavaScript (Node.js)
Framework:     Express 4.18.2
Dependencies:  express ^4.18.2, sqlite3 ^5.1.6
Domain:        LMS API (cursos, matrículas, pagamentos, usuários)
Architecture:  Monolítica — tudo em AppManager.js (DB init + routing + lógica numa única classe)
Source files:  3 files analyzed (app.js, AppManager.js, utils.js)
DB tables:     users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.18.2
Files:   3 analyzed | ~155 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Credenciais Hardcoded
File: src/utils.js:1-7
Description: Objeto `config` contém credenciais de produção literais: `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser: "no-reply@fullcycle.com.br"`.
Impact: Qualquer pessoa com acesso ao repositório tem acesso direto ao banco, ao gateway de pagamento (chave live) e ao SMTP de produção.
Recommendation: Mover para variáveis de ambiente via `.env` + `dotenv`: `process.env.PAYMENT_GATEWAY_KEY`.

### [CRITICAL] Senha em Texto Puro + Hash Fraco (badCrypto)
File: src/utils.js:17-23 e src/AppManager.js:18 e src/AppManager.js:68
Description: Seed insere senha "123" em texto puro (linha 18). A função `badCrypto` realiza loop de base64 10.000 vezes e retorna 10 caracteres — não é um hash criptográfico. Novos usuários criados no checkout usam `badCrypto` (linha 68).
Impact: Banco comprometido expõe todas as senhas. Base64 é encoding reversível em milissegundos. Rainbow tables tornam `badCrypto` inútil como proteção.
Recommendation: Substituir por `bcrypt` com salt: `await bcrypt.hash(password, 12)`.

### [CRITICAL] Dados do Cartão de Crédito Logados no Console
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` exibe número do cartão e chave do gateway em texto puro no log.
Impact: Logs de aplicação (arquivos, serviços como Datadog/CloudWatch) retêm dados de PCI-DSS — violação grave de conformidade. Chave de gateway exposta em log.
Recommendation: Remover o log completamente ou substituir por referência mascarada: `**** **** **** ${cc.slice(-4)}`.

### [HIGH] God Class — AppManager.js
File: src/AppManager.js:1-141
Description: Classe única concentra: inicialização do banco (DDL + seed), definição de 3 rotas, lógica de checkout completa (criação de usuário, processamento de pagamento, matrícula, auditoria) e geração de relatório financeiro.
Impact: Impossível testar checkout sem inicializar o banco inteiro. Qualquer mudança no schema do banco pode quebrar a lógica de pagamento. Zero separação de responsabilidades.
Recommendation: Decompor em `models/` (User, Course, Enrollment, Payment), `controllers/` por domínio, `routes/` separado e `config/database.js`.

### [HIGH] Lógica de Negócio no Route Handler
File: src/AppManager.js:28-78
Description: O handler de `/api/checkout` contém: validação de entrada, consulta ao banco, criação de usuário, processamento de pagamento, inserção de matrícula, inserção de log de auditoria e cache — tudo inline no callback da rota.
Impact: Lógica de checkout acoplada ao transporte HTTP. Impossível reusar em outros contextos (jobs, CLI, testes unitários).
Recommendation: Extrair para `services/CheckoutService.js` com método `checkout(data)` retornando Promise. Controller apenas chama o serviço.

### [MEDIUM] Callback Hell — 7 Níveis de Aninhamento
File: src/AppManager.js:28-78
Description: O handler de checkout aninha callbacks em 7 níveis: `app.post → db.get (course) → db.get (user) → processPaymentAndEnroll → db.run (enrollment) → db.run (payment) → db.run (audit_log)`.
Impact: Fluxo de execução impossível de rastrear. Race conditions silenciosas. Difícil adicionar tratamento de erro consistente.
Recommendation: Refatorar para `async/await` com `util.promisify` ou `better-sqlite3`.

### [MEDIUM] N+1 Query no Relatório Financeiro
File: src/AppManager.js:88-129
Description: Para cada curso, executa `db.all` de matrículas. Para cada matrícula, executa `db.get` de usuário E `db.get` de pagamento separadamente. Com N cursos e M matrículas: 1 + N + N*M*2 queries.
Impact: 10 cursos com 50 matrículas cada = 1001 queries onde poderia ser 1 JOIN.
Recommendation: Substituir por query única com JOINs: `SELECT c.title, u.name, p.amount FROM courses c JOIN enrollments e ON ... JOIN users u ON ... JOIN payments p ON ...`.

### [MEDIUM] Erro Silencioso em Deleção de Usuário
File: src/AppManager.js:131-137
Description: `DELETE FROM users` não verifica `err` do callback — retorna mensagem de sucesso mesmo em erro. A resposta literalmente documenta o problema: "as matrículas e pagamentos ficaram sujos no banco".
Impact: Usuários deletados deixam orphan records em `enrollments` e `payments`. Inconsistência de dados sem rollback ou cascade.
Recommendation: Verificar `err` no callback, usar transação para deleção em cascata, e retornar erro HTTP apropriado.

### [LOW] Cache Global Mutável Compartilhado
File: src/utils.js:9
Description: `let globalCache = {}` é um objeto mutável exportado como módulo singleton — qualquer parte do código pode modificá-lo sem controle.
Impact: Em ambiente com múltiplas requisições, o cache pode ser corrompido por writes concorrentes. Difícil de testar e debugar.
Recommendation: Encapsular em classe com métodos `get`/`set`/`clear`, ou usar biblioteca de cache com TTL (ex: `node-cache`).

### [LOW] API Deprecated — sqlite3 Callback-based
File: src/AppManager.js (todo o arquivo)
Description: Toda a interação com o banco usa a API de callbacks do `sqlite3`, padrão de 2012 que gera callback hell estrutural e é incompatível com `async/await` nativamente.
Impact: Qualquer adição de feature herda o padrão de callbacks aninhados. Dificulta migração futura.
Recommendation: Migrar para `better-sqlite3` (síncrono) ou usar `util.promisify` sobre os métodos do `sqlite3`.

================================
Total: 10 findings
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 2
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
