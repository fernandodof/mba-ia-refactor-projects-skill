================================
PHASE 1: PROJECT ANALYSIS — task-manager-api
================================
Language:      Python
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy 3.1.1, flask-cors 4.0.0, marshmallow 3.20.1, python-dotenv 1.0.0
Domain:        Task Manager API (tasks, users, categories)
Architecture:  Layered — models/routes/services/utils com separação parcial, mas com problemas sérios internos
Source files:  15 files analyzed
DB tables:     users, tasks, categories
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   15 analyzed | ~600 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hash de Senha com MD5 sem Salt
File: models/user.py:29,32
Description: set_password() e check_password() usam hashlib.md5(pwd.encode()).hexdigest() — sem salt, sem algoritmo seguro.
Impact: Banco comprometido expõe senhas de todos os usuários em segundos via rainbow tables. MD5 é considerado quebrado para uso criptográfico desde 2004.
Recommendation: Substituir por werkzeug.security (generate_password_hash / check_password_hash com bcrypt) ou hashlib.sha256 com salt aleatório via secrets.token_hex().

### [CRITICAL] Credenciais de Email Hardcoded
File: services/notification_service.py:9-10
Description: email_user = 'taskmanager@gmail.com' e email_password = 'senha123' definidos literalmente no código-fonte.
Impact: Qualquer pessoa com acesso ao repositório tem as credenciais SMTP. Se o repositório for público, as credenciais estão expostas indexadas.
Recommendation: Mover para variáveis de ambiente via .env: EMAIL_USER e EMAIL_PASSWORD lidos com os.getenv().

### [CRITICAL] SECRET_KEY Hardcoded
File: app.py:13
Description: app.config['SECRET_KEY'] = 'super-secret-key-123' definido como literal no código-fonte.
Impact: Qualquer pessoa com acesso ao repositório pode forjar tokens de sessão Flask e cookies assinados.
Recommendation: Mover para variável de ambiente: os.getenv('SECRET_KEY') com valor aleatório longo gerado por secrets.token_hex(32).

### [HIGH] Debug Mode com host='0.0.0.0' em Produção
File: app.py:34
Description: app.run(debug=True, host='0.0.0.0', port=5000) — debug ativo e exposto em todas as interfaces de rede.
Impact: O debugger interativo do Flask permite execução arbitrária de código no servidor para qualquer host na rede. Em produção, isso é equivalente a RCE (Remote Code Execution).
Recommendation: Ler debug de variável de ambiente: debug=os.getenv('DEBUG', 'false').lower() == 'true'. Nunca usar host='0.0.0.0' com debug=True.

### [HIGH] Fake JWT como Autenticação
File: routes/user_routes.py:210
Description: Token retornado no login é 'fake-jwt-token-' + str(user.id) — concatenação de string previsível, sem assinatura criptográfica.
Impact: Qualquer pessoa pode forjar um token para qualquer user_id sem precisar de credenciais. Não há como revogar ou validar tokens.
Recommendation: Implementar JWT real com biblioteca PyJWT ou flask-jwt-extended, usando SECRET_KEY segura para assinar os tokens.

### [MEDIUM] Senha Exposta na Resposta da API
File: models/user.py:16-25
Description: to_dict() inclui o campo 'password' (hash MD5) na serialização. Esse método é chamado em user_routes.py:33, user_routes.py:86 e user_routes.py:129 — expondo o hash em GET /users/:id, POST /users e PUT /users/:id.
Impact: Qualquer consumidor da API recebe o hash de senha de cada usuário. Combinado com MD5 fraco, o hash é facilmente reversível.
Recommendation: Remover 'password' do to_dict(). Criar método to_public_dict() sem campos sensíveis.

### [MEDIUM] N+1 Query em get_tasks()
File: routes/task_routes.py:41-57
Description: Para cada task retornada, executa User.query.get(t.user_id) e Category.query.get(t.category_id) dentro do loop — 2 queries extras por task.
Impact: Com 100 tasks, são ~201 queries ao banco onde poderiam ser 1-3 queries com JOIN ou eager loading.
Recommendation: Usar joinedload: Task.query.options(joinedload(Task.user), joinedload(Task.category)).all() — SQLAlchemy já tem relacionamentos definidos em Task.

### [MEDIUM] N+1 Query em summary_report()
File: routes/report_routes.py:53-68
Description: Para cada usuário, executa Task.query.filter_by(user_id=u.id).all() dentro do loop sobre User.query.all().
Impact: Com 50 usuários, são 51 queries ao banco. O relatório piora em performance conforme o sistema cresce.
Recommendation: Usar subquery ou joinedload: carregar todos os usuários com suas tasks em uma query com User.query.options(joinedload(User.tasks)).all().

### [LOW] Bare Except sem Tipo de Exceção
File: routes/task_routes.py:62,138,236; routes/user_routes.py:130,150; routes/report_routes.py:188,207,214,223
Description: Múltiplos blocos except: e except Exception sem especificar o tipo de exceção esperada, silenciando erros inesperados.
Impact: Erros de programação (AttributeError, TypeError) são mascarados como "Erro interno", impossível diagnosticar em produção.
Recommendation: Capturar exceções específicas (SQLAlchemyError, ValueError) e logar com logging.error(exc_info=True).

### [LOW] Constantes Duplicadas em Múltiplos Arquivos
File: routes/task_routes.py:110,177; models/task.py:39; utils/helpers.py:75,110-116
Description: A lista ['pending', 'in_progress', 'done', 'cancelled'] e os limites de prioridade (1-5) são repetidos em 3 arquivos diferentes. utils/helpers.py:110-116 define VALID_STATUSES, VALID_ROLES, MAX_TITLE_LENGTH etc. mas esses valores não são importados nos routes.
Impact: Mudança em um status válido exige localizar e alterar 3+ arquivos. Fácil de esquecer um e gerar inconsistência.
Recommendation: Centralizar em config/constants.py e importar de lá em todos os arquivos que precisam.

### [LOW] Dead Code — NotificationService Nunca Chamado
File: services/notification_service.py:1-49
Description: A classe NotificationService está implementada (send_email, notify_task_assigned, notify_task_overdue) mas não é importada nem chamada em nenhum outro arquivo do projeto.
Impact: Código morto aumenta superfície de ataque (credenciais hardcoded acessíveis) e confunde futuros mantenedores.
Recommendation: Remover a classe ou integrar corretamente com variáveis de ambiente antes de ativar.

================================
Total: 11 findings
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 3
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
