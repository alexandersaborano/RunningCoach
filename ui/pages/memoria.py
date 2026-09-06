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


st.set_page_config(page_title="Memória AI", page_icon="🧠", layout="wide")
aplicar_tema()
navegacao()
memory = MemoryManager()
memoria = memory.carregar_memoria()

cabecalho(
    "Memória AI",
    "Controla o que o treinador aprendeu e mantém o feedback útil, explícito e auditável.",
    "Atleta AI Coach · Inteligência",
)

colunas = st.columns(2)
with colunas[0]:
    st.subheader("Padrões do atleta")
    for indice, padrao in enumerate(memoria.get("padroes_atleta", [])):
        st.markdown(f"{indice + 1}. {padrao}")
    if not memoria.get("padroes_atleta"):
        st.info("Ainda não existem padrões registados.")
with colunas[1]:
    st.subheader("Regras de análise")
    for indice, regra in enumerate(memoria.get("regras_estilo", [])):
        st.markdown(f"{indice + 1}. {regra}")
    if not memoria.get("regras_estilo"):
        st.info("Ainda não existem regras registadas.")

with st.expander("Adicionar memória manual"):
    with st.form("adicionar_memoria"):
        tipo = st.selectbox("Tipo", ["Padrão do atleta", "Regra de análise"])
        texto = st.text_area("Descrição")
        guardar = st.form_submit_button("Guardar")
    if guardar:
        if not texto.strip():
            st.error("Escreve uma descrição antes de guardar.")
        elif tipo == "Padrão do atleta":
            memory.adicionar_padrao(texto.strip())
            st.success("Padrão guardado.")
            st.rerun()
        else:
            memory.adicionar_regra(texto.strip())
            st.success("Regra guardada.")
            st.rerun()

st.subheader("Histórico de feedback")
feedback = memoria.get("historico_feedback", [])
if feedback:
    st.dataframe(feedback, width="stretch")
else:
    st.info("Ainda não existem feedbacks guardados.")

st.subheader("Registos de recuperação")
recuperacao = memory.carregar_recuperacao()
if recuperacao:
    st.dataframe(list(recuperacao.values()), width="stretch")
else:
    st.info("Ainda não existem registos de recuperação.")
