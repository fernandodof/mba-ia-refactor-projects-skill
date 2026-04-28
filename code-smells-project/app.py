import logging
from flask import Flask
from flask_cors import CORS
from config.settings import SECRET_KEY, DEBUG
from config.database import get_db
from routes.routes import register_routes
from middlewares.error_handler import register_error_handlers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    CORS(app)
    get_db()
    register_routes(app)
    register_error_handlers(app)
    return app


if __name__ == "__main__":
    app = create_app()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(port=5000, debug=DEBUG)
