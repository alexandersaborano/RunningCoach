import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis do ficheiro .env se ele existir
load_dotenv()

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
ATHLETE_ID = os.getenv("ATHLETE_ID", "0")
INTERVALS_API_KEY = os.getenv("INTERVALS_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")