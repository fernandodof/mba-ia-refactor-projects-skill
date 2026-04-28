================================
PHASE 1: PROJECT ANALYSIS — code-smells-project
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, pedidos, usuários, itens_pedido)
Architecture:  Monolítica — 4 arquivos na raiz, sem separação clara de camadas
Source files:  4 files analyzed (~780 lines total)
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] SQL Injection via Concatenação de String — AP-01
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 127-130, 140, 149-166, 174, 188, 192, 220, 224, 280-296
Description: Múltiplas queries construídas por concatenação direta de variáveis:
  - models.py:28 → "SELECT * FROM produtos WHERE id = " + str(id)
  - models.py:47-50 → INSERT com concatenação de nome, descricao, preco, estoque, categoria
  - models.py:109-111 → login com concatenação de email e senha diretamente na query
  - models.py:285-296 → busca dinâmica concatenando termo, categoria, preco_min, preco_max
  - models.py:149-151, 157-166 → INSERT e UPDATE de pedidos/itens via concatenação
Impact: Atacante pode usar qualquer campo (q=, categoria=, email=, produto_id) para extrair ou destruir todo o banco de dados. O campo login_usuario é especialmente crítico: permite bypass de autenticação com email=foo' OR '1'='1.
Recommendation: Substituir todas as concatenações por queries parametrizadas com ? (sqlite3). Ver PB-01.

### [CRITICAL] Credenciais Hardcoded — AP-02
File: app.py:7, controllers.py:289-290, database.py:5
Description:
  - app.py:7 → SECRET_KEY = "minha-chave-super-secreta-123" literal no código
  - controllers.py:289-290 → health_check() retorna "secret_key": "minha-chave-super-secreta-123" e "db_path": "loja.db" na resposta JSON
  - database.py:5 → db_path = "loja.db" hardcoded (não configurável por variável de ambiente)
Impact: Qualquer pessoa com acesso ao repositório tem a SECRET_KEY para forjar tokens de sessão. Qualquer cliente que chamar /health obtém a chave secreta e o caminho do banco.
Recommendation: Extrair para config/settings.py com os.getenv(). Remover campos sensíveis do health check. Ver PB-02.

### [CRITICAL] Senha Armazenada em Texto Puro — AP-03
File: models.py:122-131, database.py:76-83
Description:
  - models.py:127 → INSERT de usuário armazena senha diretamente: VALUES ('...' , '"+ senha +"', ...)
  - models.py:109-111 → login compara senha diretamente na query SQL, sem hash
  - database.py:76-83 → seed insere senhas "admin123", "123456", "senha123" em texto puro
Impact: Qualquer dump do banco de dados expõe as senhas reais de todos os usuários imediatamente.
Recommendation: Usar werkzeug.security (pbkdf2:sha256) para hash e verificação — conforme decisão #6 do REFACTOR-DECISIONS.md.

### [CRITICAL] Endpoints Admin Sem Autenticação
File: app.py:47-78
Description:
  - /admin/reset-db (linha 47-57): deleta TODOS os dados do banco sem nenhuma verificação de autenticação
  - /admin/query (linha 59-78): executa SQL arbitrário enviado no body, sem autenticação
Impact: Qualquer pessoa que conheça a URL pode apagar todos os dados ou executar qualquer comando SQL no banco — incluindo DROP TABLE.
Recommendation: Proteger ambos os endpoints com Authorization: Bearer <ADMIN_TOKEN> via variável de ambiente — conforme decisões #1, #2 e #7 do REFACTOR-DECISIONS.md.

### [HIGH] God Module — models.py — AP-04
File: models.py:1-314
Description: Arquivo único com 314 linhas misturando queries SQL para 4 domínios distintos (produto, usuario, pedido, relatorio) sem nenhuma separação. Inclui também lógica de negócio (cálculo de desconto em relatorio_vendas, linhas 256-262) misturada com acesso a dados.
Impact: Impossível testar qualquer domínio em isolamento. Alteração em queries de produto pode afetar lógica de pedido. Lógica de desconto está escondida dentro de uma função de modelo.
Recommendation: Separar em models/produto_model.py, models/usuario_model.py, models/pedido_model.py. Mover cálculo de desconto para controllers/pedido_controller.py. Ver PB-04.

### [HIGH] Debug Mode em Produção — AP-06
File: app.py:8, app.py:88
Description:
  - app.py:8 → app.config["DEBUG"] = True hardcoded
  - app.py:88 → app.run(host="0.0.0.0", port=5000, debug=True) — expõe debugger interativo para toda a rede
Impact: O Werkzeug debugger interativo fica acessível na rede inteira. Permite execução arbitrária de código remoto no servidor por qualquer pessoa com acesso à porta 5000.
Recommendation: Ler de os.getenv("DEBUG", "false") e nunca usar host="0.0.0.0" em produção sem firewall. Ver PB-02.

### [HIGH] Lógica de Negócio no Controller — AP-05
File: controllers.py:52-54, controllers.py:242-250
Description:
  - controllers.py:52-54 → lista de categorias válidas hardcoded dentro do handler criar_produto
  - controllers.py:242-250 → lógica de notificação de status (aprovado/cancelado) misturada com o handler HTTP
Impact: Regras de negócio acopladas ao transporte HTTP. Categorias válidas duplicadas em relação a qualquer outra camada. Impossível reusar ou testar em isolamento.
Recommendation: Extrair categorias para config/constants.py. Extrair lógica de notificação para controller ou service separado. Ver PB-05 e PB-10.

### [MEDIUM] N+1 Query em get_pedidos_usuario e get_todos_pedidos — AP-07
File: models.py:171-233
Description:
  - models.py:171-201 → get_pedidos_usuario: para cada pedido executa cursor2 para buscar itens, depois cursor3 para cada item buscar nome do produto — 3 níveis de queries aninhadas
  - models.py:203-233 → get_todos_pedidos: mesma estrutura N+1 repetida
Impact: Com 100 pedidos com 5 itens cada, são 601 queries onde poderiam ser 2 JOINs. Degrada fortemente com volume.
Recommendation: Substituir por JOIN: SELECT pedidos.*, itens_pedido.*, produtos.nome FROM pedidos LEFT JOIN itens_pedido ON ... LEFT JOIN produtos ON ... Agrupar em Python. Ver PB-06.

### [MEDIUM] Dados Sensíveis Expostos na Resposta da API — AP-08
File: models.py:79-87, models.py:95-103, controllers.py:285-290
Description:
  - models.py:79-87 → get_todos_usuarios() serializa campo "senha" em todos os registros retornados
  - models.py:95-103 → get_usuario_por_id() também serializa campo "senha"
  - controllers.py:285-290 → health_check() expõe "secret_key", "debug": True e "db_path" na resposta JSON
Impact: Qualquer chamada a /usuarios ou /usuarios/<id> expõe os hashes (ou texto puro) das senhas. Qualquer chamada a /health expõe a SECRET_KEY da aplicação.
Recommendation: Remover campo "senha" de todas as serializações de usuário. Limpar health_check para retornar apenas {"status": "ok", "version": "1.0.0"}. Ver PB-08.

### [MEDIUM] Configuração e Schema Misturados em database.py — AP-04 (extensão)
File: database.py:1-86
Description: database.py mistura 3 responsabilidades distintas: configuração de conexão (linhas 1-11), criação de schema DDL (linhas 13-53), e seed de dados de desenvolvimento (linhas 56-84). O db_path está hardcoded (linha 5) sem possibilidade de configurar por variável de ambiente.
Impact: Impossível separar ambiente de dev (com seed) de produção (sem seed). Schema SQL não é versionável isoladamente.
Recommendation: Separar em config/settings.py (db_path via os.getenv), config/database.py (get_db()), config/schema.sql (DDL puro) — conforme decisão #4 do REFACTOR-DECISIONS.md.

### [LOW] Bare Except sem Log Estruturado — AP-11
File: controllers.py:10-12, controllers.py:60-62, controllers.py:219
Description: Todos os blocos except usam except Exception as e: com apenas print(str(e)). Sem stack trace, sem contexto, sem nível de log adequado. Linha 219: "ERRO CRITICO ao criar pedido" com print() em vez de logging.error().
Impact: Em produção, erros reais são invisíveis. Impossível rastrear causa raiz sem stack trace.
Recommendation: Usar logging.error(msg, exc_info=True) em vez de print(). Ver PB-09.

### [LOW] Magic Numbers e Constantes Espalhadas — AP-12
File: controllers.py:52-54, controllers.py:242
Description:
  - controllers.py:52-54 → lista ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"] hardcoded dentro da função criar_produto
  - controllers.py:242 → lista ["pendente", "aprovado", "enviado", "entregue", "cancelado"] hardcoded dentro de atualizar_status_pedido
Impact: Se uma categoria ou status for adicionado, é necessário achar e editar todos os pontos manualmente. Risco de inconsistência.
Recommendation: Centralizar em config/constants.py como VALID_CATEGORIAS e VALID_STATUS. Ver PB-10.

================================
Total: 12 findings
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2
================================
