import json
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.settings import DATA_DIR
from core.memory_manager import MemoryManager
from core.performance_analytics import (
    aggregate_weekly,
    compare_equivalent_periods,
    consolidated_export_data,
    filter_sessions,
)
from core.planned_workouts import PlannedWorkoutStore
from ui.theme import aplicar_tema, cabecalho, navegacao
from ui.table_actions import tabela_com_acoes


st.set_page_config(page_title="Performance", page_icon="📈", layout="wide")
aplicar_tema()
navegacao()
cabecalho(
    "Performance",
    "Analisa semanas, blocos de treino e tendências com filtros avançados.",
    "Atleta AI Coach · Métricas",
)

memory = MemoryManager()
sessoes = memory.carregar_historico_sessoes()
recuperacao = memory.carregar_recuperacao()
memoria = memory.carregar_memoria()
analises = memory.carregar_analises_globais()
planeados = PlannedWorkoutStore(DATA_DIR / "treinos_planeados.json").list()

def enriquecer_sessao(sessao):
    item = dict(sessao)
    data = str(item.get("data", ""))[:10]
    rec = recuperacao.get(data, {})
    item["recovery"] = (
        "low" if rec.get("recuperacao", 0) <= 4
        else "high" if rec.get("recuperacao", 0) >= 8
        else "moderate" if rec else "unknown"
    )
    item["has_analysis"] = bool(item.get("analise"))
    item["prescription_status"] = (
        "prescribed" if item.get("prescricao") else "not_prescribed"
    )
    return item


enriquecidas = [enriquecer_sessao(sessao) for sessao in sessoes]
if not enriquecidas:
    st.info("Importa ou guarda sessões para começar a explorar a performance.")
    st.stop()

datas = [str(item.get("data", ""))[:10] for item in enriquecidas if item.get("data")]
data_min = pd.to_datetime(min(datas)).date()
data_max = pd.to_datetime(max(datas)).date()

st.subheader("Filtros avançados")
filtros = st.columns(4)
with filtros[0]:
    periodo = st.date_input(
        "Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
        key="performance_periodo",
    )
with filtros[1]:
    tipos = sorted({str(item.get("tipo") or item.get("type") or "Desconhecido") for item in enriquecidas})
    tipo = st.multiselect("Tipo de treino", tipos, default=tipos, key="performance_tipo")
with filtros[2]:
    intensidades = st.multiselect(
        "Intensidade",
        ["easy", "moderate", "hard", "unknown"],
        default=["easy", "moderate", "hard", "unknown"],
        key="performance_intensidade",
    )
with filtros[3]:
    recuperacoes = st.multiselect(
        "Recuperação",
        ["low", "moderate", "high", "unknown"],
        default=["low", "moderate", "high", "unknown"],
        key="performance_recuperacao",
    )

inicio, fim = (periodo if isinstance(periodo, tuple) and len(periodo) == 2 else (data_min, data_max))
filtradas = filter_sessions(
    enriquecidas,
    start=inicio,
    end=fim,
    workout_type=tipo,
    intensity=intensidades,
    recovery=recuperacoes,
)
prescricao = st.checkbox("Apenas sessões com prescrição", value=False)
if prescricao:
    filtradas = [item for item in filtradas if item.get("prescription_status") == "prescribed"]
com_analise = st.checkbox("Apenas sessões com análise AI", value=False)
if com_analise:
    filtradas = [item for item in filtradas if item.get("has_analysis")]

st.caption(f"{len(filtradas)} sessão(ões) correspondem aos filtros.")
semanas = aggregate_weekly(filtradas)
if semanas:
    st.subheader("Dashboard semanal")
    weekly_df = pd.DataFrame(semanas)
    weekly_df["Semana"] = weekly_df.pop("week_start")
    metricas = weekly_df.iloc[-1]
    cards = st.columns(5)
    cards[0].metric("Sessões", int(metricas["session_count"]))
    cards[1].metric("Distância", f"{metricas['distance_km']:.1f} km")
    cards[2].metric("Carga", f"{metricas['load']:.0f} TSS")
    cards[3].metric("Pace médio", metricas["average_pace_min_km"] or "—")
    cards[4].metric("FC média", metricas["average_heartrate"] or "—")
    tabela_com_acoes(weekly_df, key="performance_semanal", file_stem="performance_semanal")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=weekly_df["Semana"], y=weekly_df["distance_km"], name="Distância (km)"))
    fig.add_trace(go.Scatter(x=weekly_df["Semana"], y=weekly_df["load"], name="Carga (TSS)", yaxis="y2"))
    fig.update_layout(
        title="Tendência semanal",
        yaxis={"title": "Distância (km)"},
        yaxis2={"title": "Carga (TSS)", "overlaying": "y", "side": "right"},
    )
    st.plotly_chart(fig, width="stretch")

    if len(filtradas) >= 2:
        atual = [item for item in filtradas if str(item.get("data", ""))[:10] >= semanas[-1]["week_start"]]
        anterior = [item for item in filtradas if str(item.get("data", ""))[:10] < semanas[-1]["week_start"]]
        comparacao = compare_equivalent_periods(atual, anterior)
        tabela_com_acoes(
            pd.DataFrame([
                {"Métrica": chave, "Atual": valor, "Anterior": comparacao["previous"].get(chave), "Variação": comparacao["delta"].get(chave)}
                for chave, valor in comparacao["current"].items()
            ]),
            key="performance_comparacao",
            file_stem="comparacao_blocos",
            title="Comparação de blocos",
        )
else:
    st.info("Não existem dados suficientes para os filtros selecionados.")

st.subheader("Exportação consolidada")
registos = consolidated_export_data(
    filtradas,
    analyses=analises,
    feedback=memoria.get("historico_feedback", []),
    planned=planeados,
)
tabela_com_acoes(
    pd.DataFrame(registos),
    key="performance_consolidado",
    file_stem="atleta_consolidado",
)
