import logging
from werkzeug.security import generate_password_hash, check_password_hash
from models import usuario_model

logger = logging.getLogger(__name__)


def listar_usuarios():
    usuarios = usuario_model.get_todos_usuarios()
    return {"dados": usuarios, "sucesso": True}, 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.get_usuario_por_id(usuario_id)
    if not usuario:
        return {"erro": "Usuário não encontrado"}, 404
    return {"dados": usuario, "sucesso": True}, 200


def criar_usuario(nome, email, senha):
    if not nome or not email or not senha:
        return {"erro": "Nome, email e senha são obrigatórios"}, 400

    senha_hash = generate_password_hash(senha, method="pbkdf2:sha256")
    usuario_id = usuario_model.inserir_usuario(nome, email, senha_hash)
    logger.info("Usuário criado: id=%s email=%s", usuario_id, email)
    return {"dados": {"id": usuario_id}, "sucesso": True}, 201


def login(email, senha):
    if not email or not senha:
        return {"erro": "Email e senha são obrigatórios"}, 400

    row = usuario_model.get_usuario_por_email(email)
    if row and check_password_hash(row["senha"], senha):
        logger.info("Login bem-sucedido: %s", email)
        return {
            "dados": {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]},
            "sucesso": True,
            "mensagem": "Login OK",
        }, 200

    logger.warning("Login falhou: %s", email)
    return {"erro": "Email ou senha inválidos", "sucesso": False}, 401
