import os
import socket
from dotenv import load_dotenv

load_dotenv()

def mysql_reachable(host: str, port: int, timeout: float = 0.75) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

# Prefer SQLite by default; use MySQL only if explicitly configured and reachable
DB_USER = os.getenv('DB_USER')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_NAME = os.getenv('DB_NAME', 'py_data_app')

# Support both DB_PASS and DB_PASSWORD env vars
DB_PASSWORD = os.getenv('DB_PASSWORD', os.getenv('DB_PASS', ''))

USE_SQLITE = os.getenv('USE_SQLITE', '').lower() in ('1', 'true', 'yes')

if not USE_SQLITE and DB_USER and mysql_reachable(DB_HOST, DB_PORT):
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///py_data_app.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
