import functools
from flask import request, jsonify
from config.settings import ADMIN_TOKEN


def require_admin_token(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {ADMIN_TOKEN}":
            return jsonify({"erro": "Não autorizado"}), 401
        return f(*args, **kwargs)
    return decorated
