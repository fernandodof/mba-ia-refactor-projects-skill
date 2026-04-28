import logging
from config.database import get_db
from config.constants import VALID_STATUS_PEDIDO
from models import pedido_model, produto_model

logger = logging.getLogger(__name__)


def criar_pedido(usuario_id, itens):
    if not usuario_id:
        return {"erro": "usuario_id é obrigatório"}, 400
    if not itens:
        return {"erro": "Pedido deve ter pelo menos 1 item"}, 400

    db = get_db()
    cursor = db.cursor()

    total = 0
    itens_validados = []
    for item in itens:
        produto = produto_model.get_produto_por_id(item["produto_id"])
        if not produto:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}, 400
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}, 400
        total += produto["preco"] * item["quantidade"]
        itens_validados.append((item["produto_id"], item["quantidade"], produto["preco"]))

    pedido_id = pedido_model.inserir_pedido(usuario_id, total, cursor)
    for produto_id, quantidade, preco_unitario in itens_validados:
        pedido_model.inserir_item_pedido(pedido_id, produto_id, quantidade, preco_unitario, cursor)
        produto_model.decrementar_estoque(produto_id, quantidade, cursor)

    db.commit()
    logger.info("Pedido criado: id=%s usuario=%s total=%.2f", pedido_id, usuario_id, total)
    return {"dados": {"pedido_id": pedido_id, "total": total}, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201


def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_model.get_pedidos_usuario(usuario_id)
    return {"dados": pedidos, "sucesso": True}, 200


def listar_todos_pedidos():
    pedidos = pedido_model.get_todos_pedidos()
    return {"dados": pedidos, "sucesso": True}, 200


def atualizar_status_pedido(pedido_id, novo_status):
    if novo_status not in VALID_STATUS_PEDIDO:
        return {"erro": f"Status inválido. Válidos: {VALID_STATUS_PEDIDO}"}, 400

    pedido_model.atualizar_status(pedido_id, novo_status)
    logger.info("Status do pedido %s atualizado para %s", pedido_id, novo_status)
    return {"sucesso": True, "mensagem": "Status atualizado"}, 200


def relatorio_vendas():
    dados = pedido_model.get_relatorio_vendas()
    faturamento = dados["faturamento_bruto"]
    desconto = _calcular_desconto(faturamento)
    total_pedidos = dados["total_pedidos"]

    dados["desconto_aplicavel"] = round(desconto, 2)
    dados["faturamento_liquido"] = round(faturamento - desconto, 2)
    dados["ticket_medio"] = round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
    return {"dados": dados, "sucesso": True}, 200


def _calcular_desconto(faturamento):
    if faturamento > 10000:
        return faturamento * 0.1
    if faturamento > 5000:
        return faturamento * 0.05
    if faturamento > 1000:
        return faturamento * 0.02
    return 0
