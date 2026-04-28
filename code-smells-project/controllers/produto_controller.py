import logging
from models import produto_model
from config.constants import VALID_CATEGORIAS, NOME_MIN_LEN, NOME_MAX_LEN

logger = logging.getLogger(__name__)


def listar_produtos():
    produtos = produto_model.get_todos_produtos()
    return {"dados": produtos, "sucesso": True}, 200


def buscar_produto(produto_id):
    produto = produto_model.get_produto_por_id(produto_id)
    if not produto:
        return {"erro": "Produto não encontrado", "sucesso": False}, 404
    return {"dados": produto, "sucesso": True}, 200


def buscar_produtos(termo, categoria, preco_min, preco_max):
    resultados = produto_model.buscar_produtos(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200


def criar_produto(nome, descricao, preco, estoque, categoria):
    if not nome or preco is None or estoque is None:
        return {"erro": "Nome, preço e estoque são obrigatórios"}, 400
    if preco < 0:
        return {"erro": "Preço não pode ser negativo"}, 400
    if estoque < 0:
        return {"erro": "Estoque não pode ser negativo"}, 400
    if len(nome) < NOME_MIN_LEN:
        return {"erro": "Nome muito curto"}, 400
    if len(nome) > NOME_MAX_LEN:
        return {"erro": "Nome muito longo"}, 400
    if categoria not in VALID_CATEGORIAS:
        return {"erro": f"Categoria inválida. Válidas: {VALID_CATEGORIAS}"}, 400

    produto_id = produto_model.inserir_produto(nome, descricao, preco, estoque, categoria)
    logger.info("Produto criado: id=%s nome=%s", produto_id, nome)
    return {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}, 201


def atualizar_produto(produto_id, nome, descricao, preco, estoque, categoria):
    if not produto_model.get_produto_por_id(produto_id):
        return {"erro": "Produto não encontrado"}, 404
    if not nome or preco is None or estoque is None:
        return {"erro": "Nome, preço e estoque são obrigatórios"}, 400
    if preco < 0:
        return {"erro": "Preço não pode ser negativo"}, 400
    if estoque < 0:
        return {"erro": "Estoque não pode ser negativo"}, 400

    produto_model.atualizar_produto(produto_id, nome, descricao, preco, estoque, categoria)
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


def deletar_produto(produto_id):
    if not produto_model.get_produto_por_id(produto_id):
        return {"erro": "Produto não encontrado"}, 404
    produto_model.deletar_produto(produto_id)
    logger.info("Produto deletado: id=%s", produto_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200
