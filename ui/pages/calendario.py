import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import streamlit as st

from config.settings import DATA_DIR
from core.memory_manager import MemoryManager
from core.planned_workouts import PlannedWorkoutError, PlannedWorkoutStore, merge_planned_completed
from ui.theme import aplicar_tema, cabecalho, navegacao


st.set_page_config(page_title="Calendário", page_icon="🗓️", layout="wide")
aplicar_tema()
navegacao()
cabecalho(
    "Calendário de treino",
    "Confronta o que estava planeado com o que foi realizado.",
    "Atleta AI Coach · Planeamento",
)

store = PlannedWorkoutStore(DATA_DIR / "treinos_planeados.json")
memory = MemoryManager()

st.subheader("Adicionar treino futuro")
with st.form("novo_treino_planeado"):
    colunas = st.columns(3)
    with colunas[0]:
        data_treino = st.date_input("Data", min_value=date.today())
        nome = st.text_input("Nome", placeholder="Ex.: séries de 1 km")
    with colunas[1]:
        tipo = st.text_input("Tipo", value="Run")
        distancia = st.number_input("Distância (km)", min_value=0.0, step=0.1)
    with colunas[2]:
        duracao = st.number_input("Duração (min)", min_value=0.0, step=1.0)
        notas = st.text_area("Prescrição / notas")
    criar = st.form_submit_button("Guardar treino futuro")
if criar:
    try:
        store.create({
            "date": data_treino.isoformat(),
            "name": nome,
            "workout_type": tipo,
            "distance_km": distancia or None,
            "duration_min": duracao or None,
            "prescription": notas,
        })
    except PlannedWorkoutError as error:
        st.error(str(error))
    else:
        st.success("Treino futuro guardado.")
        st.rerun()

planeados = store.list()
realizados = memory.carregar_historico_sessoes()
calendario = merge_planned_completed(planeados, realizados)
datas_realizadas = {str(item.get("data", ""))[:10] for item in realizados}
st.subheader("Calendário")
if calendario:
    linhas = []
    for item in calendario:
        linhas.append({
            "Data": str(item.get("date") or item.get("data", ""))[:10],
            "Nome": item.get("name") or item.get("nome", "Sem nome"),
            "Tipo": item.get("workout_type") or item.get("tipo", "—"),
            "Estado": "Planeado" if item.get("source") == "planned" else "Realizado",
            "Distância (km)": item.get("distance_km") or item.get("distancia_km"),
            "Prescrição": item.get("prescription") or item.get("prescricao", ""),
            "Correspondência": (
                "Realizado na data"
                if item.get("source") == "planned"
                and item.get("date") in datas_realizadas
                else "Sem sessão correspondente"
                if item.get("source") == "planned"
                else "—"
            ),
        })
    st.dataframe(pd.DataFrame(linhas), width="stretch")
else:
    st.info("Ainda não existem treinos planeados ou realizados.")

if planeados:
    st.subheader("Gerir treinos futuros")
    opcoes = {f"{item['date']} · {item.get('name', 'Sem nome')}": item["id"] for item in planeados}
    selecionado = st.selectbox("Treino", list(opcoes))
    if st.button("Apagar treino futuro"):
        store.delete(opcoes[selecionado])
        st.success("Treino futuro apagado.")
        st.rerun()
