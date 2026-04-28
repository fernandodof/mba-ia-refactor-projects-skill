import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY não definida nas variáveis de ambiente")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
if not ADMIN_TOKEN:
    raise ValueError("ADMIN_TOKEN não definido nas variáveis de ambiente")

DATABASE_URL = os.getenv("DATABASE_URL", "loja.db")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
