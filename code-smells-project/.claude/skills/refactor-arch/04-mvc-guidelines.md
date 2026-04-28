# MVC Guidelines — Arquitetura Alvo

Use este guia na **Fase 3** para orientar a reestruturação do projeto para o padrão MVC.
As regras são agnósticas de tecnologia — aplicam-se a Python/Flask e Node.js/Express.

---

## 1. Estrutura de Diretórios Alvo

### Python / Flask

```
src/
├── config/
│   └── settings.py          ← variáveis de ambiente, constantes globais
├── models/
│   ├── usuario_model.py      ← acesso a dados + queries para a entidade Usuario
│   ├── produto_model.py
│   └── pedido_model.py
├── controllers/
│   ├── usuario_controller.py ← orquestração de fluxo para Usuario
│   ├── produto_controller.py
│   └── pedido_controller.py
├── routes/
│   └── routes.py             ← mapeamento URL → controller (sem lógica)
├── middlewares/
│   └── error_handler.py      ← handler centralizado de erros HTTP
└── app.py                    ← composition root: cria app, registra rotas, middlewares
```

### Node.js / Express

```
src/
├── config/
│   └── settings.js           ← process.env, constantes globais
├── models/
│   ├── userModel.js
│   ├── courseModel.js
│   └── paymentModel.js
├── controllers/
│   ├── userController.js
│   ├── courseController.js
│   └── checkoutController.js
├── routes/
│   ├── userRoutes.js
│   └── checkoutRoutes.js
├── middlewares/
│   └── errorHandler.js
└── app.js                    ← composition root
```

---

## 2. Responsabilidades por Camada

### Config (`config/settings.py` ou `config/settings.js`)

**Deve conter:**
- Leitura de variáveis de ambiente (`os.getenv`, `process.env`)
- Constantes globais da aplicação (STATUS válidos, PRIORIDADES, CATEGORIAS)
- Configuração do banco de dados (connection string, pool size)

**Não deve conter:**
- Lógica de negócio
- Queries SQL
- Handlers de rota

```python
# Python — exemplo
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-key")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

VALID_STATUS = ["pendente", "em_andamento", "concluido"]
PRIORITY_MIN = 1
PRIORITY_MAX = 5
```

---

### Model (`models/`)

**Deve conter:**
- Definição da entidade (campos, tipos)
- Queries parametrizadas para CRUD da entidade
- Método `to_dict()` sem campos sensíveis

**Não deve conter:**
- Lógica de negócio (cálculos, regras de desconto, validações de negócio)
- Lógica de rota ou HTTP
- Imports de Flask/Express

```python
# Python — exemplo
def get_produto_por_id(produto_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    return cursor.fetchone()
```

---

### Controller (`controllers/`)

**Deve conter:**
- Receber dados validados da rota
- Chamar model(s) para buscar/persistir dados
- Aplicar regras de negócio simples
- Retornar resposta HTTP (status code + JSON)

**Não deve conter:**
- Queries SQL diretas
- Definição de rotas (`@app.route`, `app.get`)
- Leitura de `request` diretamente (recebe dados já extraídos)

```python
# Python — exemplo
def criar_produto(nome, preco, categoria, estoque):
    if not nome or preco <= 0:
        return {"error": "Dados inválidos"}, 400
    produto_id = produto_model.inserir_produto(nome, preco, categoria, estoque)
    return {"id": produto_id, "nome": nome}, 201
```

---

### Routes (`routes/`)

**Deve conter:**
- Mapeamento de URL para controller
- Extração de parâmetros do request (`request.json`, `req.body`)
- Validação de tipos básica (campo obrigatório presente ou não)

**Não deve conter:**
- Queries SQL
- Lógica de negócio
- Mais de 10 linhas por handler

```python
# Python — exemplo com Flask Blueprint
from flask import Blueprint, request, jsonify
from controllers import produto_controller

produtos_bp = Blueprint("produtos", __name__)

@produtos_bp.route("/produtos", methods=["POST"])
def criar():
    data = request.get_json()
    result, status = produto_controller.criar_produto(
        data.get("nome"), data.get("preco"),
        data.get("categoria"), data.get("estoque", 0)
    )
    return jsonify(result), status
```

---

### Middleware (`middlewares/`)

**Deve conter:**
- Handler centralizado de erros HTTP
- Autenticação/autorização (verificar token)
- Logging de requests
- CORS

**Não deve conter:**
- Lógica de negócio
- Queries SQL

```python
# Python — exemplo de error handler Flask
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Erro interno do servidor"}), 500
```

---

### App / Entry Point (`app.py` ou `app.js`)

**Deve conter apenas:**
- Criação da instância da aplicação
- Registro de rotas (blueprints, routers)
- Registro de middlewares
- Inicialização do banco de dados
- `app.run()` / `app.listen()`

**Não deve conter:**
- Definição de rotas inline
- Lógica de negócio
- Queries SQL
- Credenciais hardcoded

```python
# Python — exemplo de composition root limpo
from flask import Flask
from config.settings import SECRET_KEY, DEBUG
from routes.routes import register_routes
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    register_routes(app)
    register_error_handlers(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=DEBUG)
```

---

## 3. Regras Proibidas (Violações de MVC)

| Proibido | Camada violada | Correção |
|---|---|---|
| Query SQL em controller ou route | Model | Mover para model |
| Lógica de negócio em model | Controller | Mover para controller |
| `@app.route` com >15 linhas de lógica | Route | Extrair para controller |
| Credencial literal em qualquer arquivo | Config | Mover para `.env` |
| `debug=True` hardcoded | Config | Ler de `os.getenv("DEBUG")` |
| `password` em `to_dict()` | Model | Excluir campo sensível |
| `cursor.execute(query + var)` | Model | Usar query parametrizada |
| Query dentro de `for` loop | Model | Usar JOIN |

---

## 4. Checklist de Validação Pós-Refatoração

```
### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados por entidade, apenas com acesso a dados
- [ ] Controllers orquestram fluxo sem queries diretas
- [ ] Routes apenas mapeiam URL → controller
- [ ] Error handling centralizado em middleware
- [ ] Entry point limpo (apenas wiring)
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```
