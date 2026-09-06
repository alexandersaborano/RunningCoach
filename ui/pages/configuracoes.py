import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

from config.settings import (
    ANTHROPIC_API_KEY,
    ATHLETE_ID,
    GEMINI_API_KEY,
    INTERVALS_API_KEY,
    OPENAI_API_KEY,
)
from core.intervals_client import IntervalsClient
from core.ai_agents import AGENT_DEFINITIONS
from ui.theme import aplicar_tema, cabecalho, navegacao


st.set_page_config(page_title="Configurações", page_icon="⚙️", layout="wide")
aplicar_tema()
navegacao()

cabecalho(
    "Configurações",
    "Mantém as integrações e o armazenamento local prontos para o próximo treino.",
    "Atleta AI Coach · Sistema",
)

st.subheader("Estado das integrações")
colunas = st.columns(5)
colunas[0].metric("Gemini", "Configurado" if GEMINI_API_KEY else "Em falta")
colunas[1].metric("Intervals.icu", "Configurado" if INTERVALS_API_KEY else "Em falta")
colunas[2].metric("ID atleta", "Configurado" if ATHLETE_ID and ATHLETE_ID != "0" else "Em falta")
colunas[3].metric("OpenAI", "Configurado" if OPENAI_API_KEY else "Opcional")
colunas[4].metric("Anthropic", "Configurado" if ANTHROPIC_API_KEY else "Opcional")

st.info(
    "A aplicação está configurada para utilização local. "
    "As chaves são lidas do ficheiro .env e os dados ficam na pasta data/."
)

st.subheader("Agentes especializados")
for agente in AGENT_DEFINITIONS:
    st.write(f"**{agente.name.title()}** — {agente.provider}")
st.caption(
    "Para distribuir agentes por providers, define AGENT_CARGA_PROVIDER, "
    "AGENT_FISIOLOGIA_PROVIDER, AGENT_TREINO_PROVIDER ou AGENT_CRITICO_PROVIDER."
)

if st.button("🔌 Testar ligação ao Intervals.icu"):
    if not INTERVALS_API_KEY or not ATHLETE_ID or ATHLETE_ID == "0":
        st.error("Define INTERVALS_API_KEY e ATHLETE_ID no ficheiro .env.")
    else:
        with st.spinner("A testar ligação..."):
            perfil = IntervalsClient().obter_perfil_e_zonas()
        if perfil:
            st.success("Ligação ao Intervals.icu funcional.")
        else:
            st.error("Não foi possível obter o perfil. Confirma a chave e o ID do atleta.")

st.subheader("Localização dos dados")
st.caption(
    "Usa o botão de backup na barra lateral antes de alterações importantes "
    "ou executa `python backup_data.py`."
)
st.code(
    "data/perfil_atleta.json\n"
    "data/memoria_atleta.json\n"
    "data/recuperacao_atleta.json\n"
    "data/historico_sessoes/",
    language="text",
)
