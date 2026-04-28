import logging
from flask import Blueprint, request, jsonify
from controllers import produto_controller, usuario_controller, pedido_controller, admin_controller
from middlewares.auth import require_admin_token

logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__)


# ── Produtos ──────────────────────────────────────────────────────────────────

@bp.route("/produtos", methods=["GET"])
def listar_produtos():
    result, status = produto_controller.listar_produtos()
    return jsonify(result), status


@bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min", type=float)
    preco_max = request.args.get("preco_max", type=float)
    result, status = produto_controller.buscar_produtos(termo, categoria, preco_min, preco_max)
    return jsonify(result), status


@bp.route("/produtos/<int:produto_id>", methods=["GET"])
def buscar_produto(produto_id):
    result, status = produto_controller.buscar_produto(produto_id)
    return jsonify(result), status


@bp.route("/produtos", methods=["POST"])
def criar_produto():
    data = request.get_json() or {}
    result, status = produto_controller.criar_produto(
        data.get("nome", ""),
        data.get("descricao", ""),
        data.get("preco"),
        data.get("estoque"),
        data.get("categoria", "geral"),
    )
    return jsonify(result), status


@bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    data = request.get_json() or {}
    result, status = produto_controller.atualizar_produto(
        produto_id,
        data.get("nome", ""),
        data.get("descricao", ""),
        data.get("preco"),
        data.get("estoque"),
        data.get("categoria", "geral"),
    )
    return jsonify(result), status


@bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar_produto(produto_id):
    result, status = produto_controller.deletar_produto(produto_id)
    return jsonify(result), status


# ── Usuários ──────────────────────────────────────────────────────────────────

@bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    result, status = usuario_controller.listar_usuarios()
    return jsonify(result), status


@bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    result, status = usuario_controller.buscar_usuario(usuario_id)
    return jsonify(result), status


@bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    data = request.get_json() or {}
    result, status = usuario_controller.criar_usuario(
        data.get("nome", ""),
        data.get("email", ""),
        data.get("senha", ""),
    )
    return jsonify(result), status


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    result, status = usuario_controller.login(data.get("email", ""), data.get("senha", ""))
    return jsonify(result), status


# ── Pedidos ───────────────────────────────────────────────────────────────────

@bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    data = request.get_json() or {}
    result, status = pedido_controller.criar_pedido(
        data.get("usuario_id"),
        data.get("itens", []),
    )
    return jsonify(result), status


@bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    result, status = pedido_controller.listar_todos_pedidos()
    return jsonify(result), status


@bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    result, status = pedido_controller.listar_pedidos_usuario(usuario_id)
    return jsonify(result), status


@bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    data = request.get_json() or {}
    result, status = pedido_controller.atualizar_status_pedido(pedido_id, data.get("status", ""))
    return jsonify(result), status


# ── Relatórios ────────────────────────────────────────────────────────────────

@bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    result, status = pedido_controller.relatorio_vendas()
    return jsonify(result), status


# ── Health ────────────────────────────────────────────────────────────────────

@bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "versao": "2.0.0"}), 200


# ── Admin (protegido por ADMIN_TOKEN) ─────────────────────────────────────────

@bp.route("/admin/reset-db", methods=["POST"])
@require_admin_token
def reset_database():
    result, status = admin_controller.reset_db()
    return jsonify(result), status


@bp.route("/admin/query", methods=["POST"])
@require_admin_token
def executar_query():
    data = request.get_json() or {}
    result, status = admin_controller.executar_query(data.get("sql", ""))
    return jsonify(result), status


def register_routes(app):
    app.register_blueprint(bp)

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "2.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })
