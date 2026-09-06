import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

from core.memory_manager import MemoryManager
from ui.theme import aplicar_tema, cabecalho, navegacao


st.set_page_config(page_title="Análises globais", page_icon="🧭", layout="wide")
aplicar_tema()
navegacao()

cabecalho(
    "Análises globais",
    "Consulta e pesquisa as análises longitudinais guardadas localmente.",
    "Atleta AI Coach · Evolução",
)

registos = MemoryManager().listar_analises_globais()
termo = st.text_input("Pesquisar por texto, data ou atividade")
if termo.strip():
    termo = termo.casefold()
    registos = [
        registo for registo in registos
        if termo in str(registo["dados"]).casefold()
        or termo in registo["ficheiro"].casefold()
    ]

st.metric("Análises encontradas", len(registos))
if not registos:
    st.info("Ainda não existem análises globais que correspondam à pesquisa.")
else:
    for registo in registos:
        dados = registo["dados"]
        with st.expander(
            f"{registo['ficheiro']} · {len(dados.get('atividade_ids', []))} sessões"
        ):
            st.caption(f"Filtros: {dados.get('filtros', 'Não registados')}")
            st.markdown(dados.get("analise", "Sem texto de análise."))
            with st.expander("Ver contexto guardado"):
                st.json(dados)
