import os
from pathlib import Path

# Diretório Base da Aplicação
BASE_DIR = Path(__file__).resolve().parent

# Configurações de Servidor
SECRET_KEY = os.environ.get("SECRET_KEY", "webstruct_secret_key_2026_dev")
HOST = "127.0.0.1"
PORT = 5000

# Caminhos do Banco de Dados e Perfis do Chrome
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "webstruct.db"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

# Perfil Persistente do Navegador para manter logins/cookies
CHROME_PROFILE_DIR = BASE_DIR / "bot_chrome_profile"
DEPS_DIR = BASE_DIR / "deps"

# Garante que os diretórios essenciais existam
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
DEPS_DIR.mkdir(parents=True, exist_ok=True)

# Device ID (Será preenchido no Bootstrap)
DEVICE_ID = None
