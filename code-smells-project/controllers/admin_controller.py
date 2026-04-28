import logging
from config.database import get_db

logger = logging.getLogger(__name__)


def reset_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()
    logger.warning("Banco de dados resetado via /admin/reset-db")
    return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200


def executar_query(sql):
    if not sql:
        return {"erro": "Query não informada"}, 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    if sql.strip().upper().startswith("SELECT"):
        rows = cursor.fetchall()
        return {"dados": [dict(r) for r in rows], "sucesso": True}, 200
    db.commit()
    return {"mensagem": "Query executada", "sucesso": True}, 200
