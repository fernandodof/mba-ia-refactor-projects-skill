# Refactoring Playbook — Transformações por Anti-Pattern

Use este playbook na **Fase 3** para guiar cada transformação de código.
Cada padrão tem: sinal de detecção, código antes (problema), código depois (corrigido), e nota de aplicabilidade por stack.

---

## PB-01 — SQL Injection → Queries Parametrizadas {#pb-01}

**Aplica-se a:** Python/Flask com sqlite3 | Node.js com sqlite3

### Antes (Python)
```python
# CRÍTICO: concatenação direta de variável em SQL
def get_produto_por_id(id):
    cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))

def buscar_produtos(termo):
    cursor.execute("SELECT * FROM produtos WHERE nome LIKE '%" + termo + "%'")

def criar_usuario(nome, email, senha):
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha) VALUES ('" +
        nome + "', '" + email + "', '" + senha + "')"
    )
```

### Depois (Python)
```python
# CORRETO: queries parametrizadas com placeholder ?
def get_produto_por_id(produto_id):
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))

def buscar_produtos(termo):
    cursor.execute(
        "SELECT * FROM produtos WHERE nome LIKE ?",
        (f"%{termo}%",)
    )

def criar_usuario(nome, email, senha_hash):
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
        (nome, email, senha_hash)
    )
```

### Antes (Node.js)
```javascript
// CRÍTICO: template literal com variável em SQL
db.get(`SELECT * FROM users WHERE id = ${userId}`, callback)
db.run(`INSERT INTO users (name, email) VALUES ('${name}', '${email}')`, callback)
```

### Depois (Node.js)
```javascript
// CORRETO: placeholders ? com array de parâmetros
db.get("SELECT * FROM users WHERE id = ?", [userId], callback)
db.run("INSERT INTO users (name, email) VALUES (?, ?)", [name, email], callback)
```

---

## PB-02 — Credenciais Hardcoded → Variáveis de Ambiente {#pb-02}

**Aplica-se a:** Python/Flask | Node.js/Express

### Antes (Python)
```python
# CRÍTICO: credenciais literais no código
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
DB_PATH = "/app/loja.db"
SMTP_PASSWORD = "senha123"
```

### Depois (Python)
```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY não definida nas variáveis de ambiente")

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
```

```
# .env (nunca commitar — adicionar ao .gitignore)
SECRET_KEY=gerar-com-secrets.token_hex-32
DEBUG=false
DATABASE_URL=sqlite:///loja.db
SMTP_PASSWORD=senha-real-aqui
```

### Antes (Node.js)
```javascript
// CRÍTICO: credenciais em objeto de configuração no código
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    smtpUser: "no-reply@empresa.com"
}
```

### Depois (Node.js)
```javascript
// config/settings.js
require('dotenv').config()

module.exports = {
    dbPass: process.env.DB_PASS,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    smtpUser: process.env.SMTP_USER,
    debug: process.env.NODE_ENV !== 'production'
}
```

---

## PB-03 — Senha Plain-Text / Hash Fraco → Hash Seguro com Salt {#pb-03}

**Aplica-se a:** Python/Flask | Node.js/Express

### Antes (Python)
```python
# CRÍTICO: senha em texto puro
def criar_usuario(nome, email, senha):
    cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                   (nome, email, senha))  # senha sem hash!

# CRÍTICO: MD5 sem salt
import hashlib
senha_hash = hashlib.md5(senha.encode()).hexdigest()

# CRÍTICO: comparação direta
if usuario['senha'] == senha_digitada:
    return True
```

### Depois (Python)
```python
import hashlib
import os

def hash_senha(senha: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt, 100_000)
    return salt.hex() + ':' + key.hex()

def verificar_senha(senha_digitada: str, senha_armazenada: str) -> bool:
    salt_hex, key_hex = senha_armazenada.split(':')
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac('sha256', senha_digitada.encode(), salt, 100_000)
    return key.hex() == key_hex

def criar_usuario(nome, email, senha):
    senha_hash = hash_senha(senha)
    cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                   (nome, email, senha_hash))
```

### Antes (Node.js)
```javascript
// CRÍTICO: base64 repetido como "hash"
function badCrypto(str) {
    let result = str
    for (let i = 0; i < 10000; i++) {
        result = Buffer.from(result).toString('base64')
    }
    return result.substring(0, 10)
}
```

### Depois (Node.js)
```javascript
const crypto = require('crypto')

function hashSenha(senha) {
    const salt = crypto.randomBytes(32).toString('hex')
    const hash = crypto.pbkdf2Sync(senha, salt, 100000, 64, 'sha256').toString('hex')
    return `${salt}:${hash}`
}

function verificarSenha(senhaDigitada, senhaArmazenada) {
    const [salt, hash] = senhaArmazenada.split(':')
    const hashDigitado = crypto.pbkdf2Sync(senhaDigitada, salt, 100000, 64, 'sha256').toString('hex')
    return hash === hashDigitado
}
```

---

## PB-04 — God Class → Separação por Domínio {#pb-04}

**Aplica-se a:** Python/Flask | Node.js/Express

### Antes (Python)
```python
# models.py — 350 linhas com TUDO misturado
def get_produto(id): ...          # domínio produto
def criar_produto(dados): ...     # domínio produto
def get_usuario(id): ...          # domínio usuario
def autenticar_usuario(e, s): ... # domínio usuario
def criar_pedido(dados): ...      # domínio pedido
def get_itens_pedido(id): ...     # domínio pedido
def calcular_desconto(total): ... # regra de negócio
def enviar_email(dest, msg): ...  # serviço externo
```

### Depois (Python)
```python
# models/produto_model.py
def get_produto_por_id(produto_id): ...
def listar_produtos(filtros): ...
def inserir_produto(nome, preco, categoria, estoque): ...
def atualizar_produto(produto_id, dados): ...

# models/usuario_model.py
def get_usuario_por_id(usuario_id): ...
def get_usuario_por_email(email): ...
def inserir_usuario(nome, email, senha_hash): ...

# models/pedido_model.py
def get_pedidos_do_usuario(usuario_id): ...
def inserir_pedido(usuario_id, total): ...
def get_itens_do_pedido(pedido_id): ...

# controllers/pedido_controller.py
def calcular_desconto(total): ...  # regra de negócio fica no controller

# services/notification_service.py
def enviar_email(destinatario, mensagem): ...  # serviço externo isolado
```

### Antes (Node.js)
```javascript
// AppManager.js — classe única com tudo
class AppManager {
    initDb() { /* schema + seed */ }
    setupRoutes() { /* todas as rotas */ }
    processCheckout() { /* lógica de pagamento */ }
    gerarRelatorio() { /* lógica de relatório */ }
}
```

### Depois (Node.js)
```javascript
// models/userModel.js — apenas queries de usuário
// models/courseModel.js — apenas queries de curso
// controllers/checkoutController.js — lógica de checkout
// controllers/reportController.js — lógica de relatório
// routes/checkoutRoutes.js — apenas mapeamento de URL
// app.js — apenas wiring
```

---

## PB-05 — Lógica de Negócio no Route Handler → Extrair para Controller {#pb-05}

**Aplica-se a:** Python/Flask | Node.js/Express

### Antes (Python)
```python
@app.route("/pedidos", methods=["POST"])
def criar_pedido():
    data = request.get_json()
    # PROBLEMA: lógica de negócio pesada no handler
    if data["total"] > 1000:
        desconto = data["total"] * 0.1
    elif data["total"] > 500:
        desconto = data["total"] * 0.05
    else:
        desconto = 0
    total_final = data["total"] - desconto
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pedidos ...", (data["usuario_id"], total_final))
    conn.commit()
    return jsonify({"total": total_final}), 201
```

### Depois (Python)
```python
# routes/routes.py — apenas extrai parâmetros e chama controller
@pedidos_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    data = request.get_json()
    result, status = pedido_controller.criar_pedido(
        data.get("usuario_id"), data.get("total"), data.get("itens", [])
    )
    return jsonify(result), status

# controllers/pedido_controller.py — lógica de negócio aqui
def criar_pedido(usuario_id, total_bruto, itens):
    if not usuario_id or total_bruto <= 0:
        return {"error": "Dados inválidos"}, 400
    desconto = calcular_desconto(total_bruto)
    total_final = total_bruto - desconto
    pedido_id = pedido_model.inserir_pedido(usuario_id, total_final)
    return {"id": pedido_id, "total": total_final, "desconto": desconto}, 201

def calcular_desconto(total):
    if total > 1000:
        return total * 0.1
    if total > 500:
        return total * 0.05
    return 0
```

---

## PB-06 — N+1 Query → JOIN ou Eager Loading {#pb-06}

**Aplica-se a:** Python/Flask com sqlite3 | Node.js com sqlite3

### Antes (Python)
```python
# PROBLEMA: query dentro de loop — N+1
def get_todos_pedidos():
    cursor.execute("SELECT * FROM pedidos")
    pedidos = cursor.fetchall()
    resultado = []
    for pedido in pedidos:
        # query extra para cada pedido!
        cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido["id"],))
        itens = cursor.fetchall()
        resultado.append({**dict(pedido), "itens": itens})
    return resultado
```

### Depois (Python)
```python
# CORRETO: uma query com JOIN
def get_todos_pedidos():
    cursor.execute("""
        SELECT
            p.id, p.usuario_id, p.total, p.status, p.criado_em,
            i.id as item_id, i.produto_id, i.quantidade, i.preco_unitario
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        ORDER BY p.id
    """)
    rows = cursor.fetchall()
    # agrupar itens por pedido em Python
    pedidos = {}
    for row in rows:
        pid = row["id"]
        if pid not in pedidos:
            pedidos[pid] = {
                "id": pid, "usuario_id": row["usuario_id"],
                "total": row["total"], "status": row["status"], "itens": []
            }
        if row["item_id"]:
            pedidos[pid]["itens"].append({
                "id": row["item_id"], "produto_id": row["produto_id"],
                "quantidade": row["quantidade"], "preco_unitario": row["preco_unitario"]
            })
    return list(pedidos.values())
```

---

## PB-07 — Callback Hell → async/await {#pb-07}

**Aplica-se a:** Node.js/Express

### Antes (Node.js)
```javascript
// PROBLEMA: pirâmide de callbacks, 7 níveis de indentação
app.post('/checkout', (req, res) => {
    db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
        if (err) return res.status(500).json({error: err})
        db.get("SELECT * FROM courses WHERE id = ?", [courseId], (err, course) => {
            if (err) return res.status(500).json({error: err})
            db.run("INSERT INTO enrollments ...", [...], (err) => {
                if (err) return res.status(500).json({error: err})
                db.run("INSERT INTO payments ...", [...], (err) => {
                    if (err) return res.status(500).json({error: err})
                    res.json({success: true})
                })
            })
        })
    })
})
```

### Depois (Node.js)
```javascript
// CORRETO: async/await com better-sqlite3 (síncrono) ou promisify
const { promisify } = require('util')
const dbGet = promisify(db.get.bind(db))
const dbRun = promisify(db.run.bind(db))

app.post('/checkout', async (req, res) => {
    try {
        const user = await dbGet("SELECT * FROM users WHERE email = ?", [email])
        if (!user) return res.status(404).json({error: 'Usuário não encontrado'})

        const course = await dbGet("SELECT * FROM courses WHERE id = ?", [courseId])
        if (!course) return res.status(404).json({error: 'Curso não encontrado'})

        await dbRun("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
                    [user.id, course.id])
        await dbRun("INSERT INTO payments (user_id, amount) VALUES (?, ?)",
                    [user.id, course.price])

        res.json({success: true, courseId: course.id})
    } catch (err) {
        console.error('Checkout error:', err)
        res.status(500).json({error: 'Erro interno no checkout'})
    }
})
```

---

## PB-08 — Dados Sensíveis na Resposta → Serialização Explícita {#pb-08}

**Aplica-se a:** Python/Flask | Node.js/Express

### Antes (Python)
```python
# PROBLEMA: to_dict() expõe senha e dados internos
class Usuario:
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,      # expõe hash da senha!
            "tipo": self.tipo
        }

# PROBLEMA: health check expõe SECRET_KEY
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "secret_key": app.config["SECRET_KEY"],  # expõe chave!
        "db_path": DATABASE_PATH
    })
```

### Depois (Python)
```python
# CORRETO: serialização com campos explícitos e seguros
class Usuario:
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo
            # senha nunca incluída
        }

    def to_dict_public(self):
        """Versão para respostas públicas (sem tipo interno)."""
        return {"id": self.id, "nome": self.nome, "email": self.email}

# CORRETO: health check sem dados sensíveis
@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})
```

### Antes (Node.js)
```javascript
// PROBLEMA: retorna objeto completo com campos sensíveis
res.json(user)  // user tem password, internal_token, etc.
```

### Depois (Node.js)
```javascript
// CORRETO: desestrutura apenas os campos públicos
const { id, name, email, role } = user
res.json({ id, name, email, role })
```

---

## PB-09 — Bare Except → Except Específico com Logging {#pb-09}

**Aplica-se a:** Python/Flask

### Antes (Python)
```python
# PROBLEMA: bare except engole qualquer erro silenciosamente
try:
    resultado = model.criar_produto(dados)
except:
    return jsonify({"error": "Erro interno"}), 500

# PROBLEMA: except genérico sem log útil
try:
    conn.commit()
except Exception as e:
    print(e)  # só print, sem stack trace, sem contexto
    pass
```

### Depois (Python)
```python
import logging

logger = logging.getLogger(__name__)

# CORRETO: exceção específica com log estruturado
try:
    resultado = model.criar_produto(dados)
except ValueError as e:
    logger.warning("Dados inválidos na criação de produto: %s", e)
    return jsonify({"error": str(e)}), 400
except Exception as e:
    logger.error("Erro inesperado ao criar produto", exc_info=True)
    return jsonify({"error": "Erro interno do servidor"}), 500
```

---

## PB-10 — Constantes Espalhadas → Módulo de Configuração Centralizado {#pb-10}

**Aplica-se a:** Python/Flask | Node.js/Express

### Antes (Python)
```python
# models/task.py linha 39
VALID_STATUS = ["pendente", "em_andamento", "concluido"]

# routes/task_routes.py linha 110
valid_statuses = ["pendente", "em_andamento", "concluido"]  # duplicado!

# utils/helpers.py linha 110
STATUS_VALIDOS = ["pendente", "em_andamento", "concluido"]  # triplicado!

# routes/task_routes.py linha 113
if prioridade < 1 or prioridade > 5:  # magic numbers!
```

### Depois (Python)
```python
# config/constants.py — fonte única da verdade
VALID_STATUS = ["pendente", "em_andamento", "concluido", "cancelado"]
PRIORITY_MIN = 1
PRIORITY_MAX = 5
VALID_CATEGORIES = ["bug", "feature", "melhoria", "documentacao"]
DEFAULT_PAGE_SIZE = 20

# Em todos os outros arquivos:
from config.constants import VALID_STATUS, PRIORITY_MIN, PRIORITY_MAX

if status not in VALID_STATUS:
    return {"error": f"Status inválido. Use: {VALID_STATUS}"}, 400

if not (PRIORITY_MIN <= prioridade <= PRIORITY_MAX):
    return {"error": f"Prioridade deve ser entre {PRIORITY_MIN} e {PRIORITY_MAX}"}, 400
```

### Antes (Node.js)
```javascript
// Validações repetidas em vários arquivos
if (!['active', 'inactive', 'pending'].includes(status)) { ... }
```

### Depois (Node.js)
```javascript
// config/constants.js
module.exports = {
    VALID_STATUS: ['active', 'inactive', 'pending'],
    PAYMENT_STATUS: ['PAID', 'DENIED', 'PENDING'],
    MAX_PAGE_SIZE: 50
}

// Em qualquer arquivo:
const { VALID_STATUS } = require('../config/constants')
if (!VALID_STATUS.includes(status)) { ... }
```
