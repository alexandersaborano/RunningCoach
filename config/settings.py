import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis do ficheiro .env se ele existir
load_dotenv()


def _streamlit_secret(name: str):
    """Lê um secret do Streamlit sem tornar o modo local dependente dele."""
    try:
        import streamlit as st
        from streamlit.errors import StreamlitSecretNotFoundError
    except ImportError:
        return None

    try:
        value = st.secrets.get(name)
    except StreamlitSecretNotFoundError:
        return None
    return value if isinstance(value, str) else None


def _config_value(name: str, default: str = "") -> str:
    secret = _streamlit_secret(name)
    if secret is not None:
        return secret.strip()
    return os.getenv(name, default).strip()

# Caminhos de Pastas
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HISTORICO_DIR = DATA_DIR / "historico_sessoes"

DATA_DIR.mkdir(exist_ok=True)
HISTORICO_DIR.mkdir(exist_ok=True)

FICHEIRO_MEMORIA = DATA_DIR / "memoria_atleta.json"
FICHEIRO_PERFIL = DATA_DIR / "perfil_atleta.json"
FICHEIRO_RECUPERACAO = DATA_DIR / "recuperacao_atleta.json"
ANALISES_GLOBAIS_DIR = DATA_DIR / "analises_globais"

# Credenciais
ATHLETE_ID = _config_value("ATHLETE_ID", "0")
INTERVALS_API_KEY = _config_value("INTERVALS_API_KEY")
GEMINI_API_KEY = _config_value("GEMINI_API_KEY")
OPENAI_API_KEY = _config_value("OPENAI_API_KEY")
ANTHROPIC_API_KEY = _config_value("ANTHROPIC_API_KEY")