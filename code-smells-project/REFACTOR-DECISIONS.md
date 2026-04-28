# Decisões de Refatoração — code-smells-project

Decisões tomadas antes da execução da skill `refactor-arch` (Parte 1).

| # | Decisão | Escolha |
|---|---------|---------|
| 1 | `/admin/query` perigoso | Manter, proteger com `ADMIN_TOKEN` |
| 2 | Mecanismo de autenticação admin | `Authorization: Bearer <ADMIN_TOKEN>` via env var |
| 3 | Estrutura MVC | Flat na raiz: `config/`, `models/`, `controllers/`, `routes/` |
| 4 | Separação do `database.py` | `config/settings.py` + `config/database.py` + `config/schema.sql` |
| 5 | Correção SQL Injection | Parametrização com `?` placeholders do `sqlite3` |
| 6 | Hash de senhas | `werkzeug.security` (pbkdf2:sha256) |
| 7 | `/admin/reset-db` | Proteger com mesmo `ADMIN_TOKEN` |
| 8 | Gerenciamento de env vars | `.env.example` + `os.environ.get()` + `.gitignore` |
| 9 | N+1 queries | Corrigir com JOIN nas queries de pedidos/itens |
| 10 | Validação final | `curl` inline: criar usuário → login → criar produto → criar pedido → listar pedidos |
