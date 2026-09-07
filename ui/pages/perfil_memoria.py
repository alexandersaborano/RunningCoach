import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

from core.intervals_client import IntervalsClient
from core.heart_rate_zones import calcular_zonas_hrr
from ui.theme import aplicar_tema, cabecalho, navegacao


st.set_page_config(page_title="Perfil do atleta", page_icon="👤", layout="wide")
aplicar_tema()
navegacao()

client = IntervalsClient()

cabecalho(
    "Perfil do atleta",
    "Uma visão completa das métricas, objetivos e contexto que orientam o treinador.",
    "Atleta AI Coach · Identidade",
)

perfil = client.obter_perfil_e_zonas()
if "perfil_atleta" not in st.session_state:
    st.session_state["perfil_atleta"] = perfil or {}
perfil = st.session_state["perfil_atleta"]

if st.button("🔄 Atualizar perfil do Intervals.icu"):
    with st.spinner("A sincronizar o perfil..."):
        perfil_atualizado = client.obter_perfil_e_zonas()
        if perfil_atualizado:
            st.session_state["perfil_atleta"] = perfil_atualizado
            st.success("Perfil atualizado com sucesso.")
            st.rerun()
        st.error("Não foi possível atualizar o perfil. Verifica as credenciais.")

if perfil:
    st.subheader("Perfil sincronizado")
    colunas = st.columns(3)
    colunas[0].metric("FC máxima", f"{perfil.get('max_hr', '--')} bpm")
    colunas[1].metric("Limiar", f"{perfil.get('lthr', '--')} bpm")
    colunas[2].metric("FC repouso", f"{perfil.get('resting_hr', '--')} bpm")
    st.write("Zonas de FC:", perfil.get("zonas_hr", []))
    st.caption(
        "Origem: "
        f"{perfil.get('zonas_hr_origem', 'desconhecida')} · "
        f"Método: {perfil.get('zonas_hr_metodo', 'desconhecido')}"
    )
    if perfil.get("zonas_hr_nomes"):
        st.write("Nomes das zonas:", perfil["zonas_hr_nomes"])
    st.caption(
        "As zonas sincronizadas são apresentadas sem substituir o método "
        "configurado no Garmin."
    )
    try:
        zonas_hrr = calcular_zonas_hrr(perfil.get("max_hr"), perfil.get("resting_hr"))
    except ValueError:
        zonas_hrr = []
    if zonas_hrr:
        st.write("Limites calculados por %HRR (Karvonen):", zonas_hrr)
else:
    st.warning("Não foi possível carregar o perfil do Intervals.icu.")

st.subheader("Perfil completo do atleta")
with st.form("perfil_completo"):
    perfil_colunas = st.columns(2)
    with perfil_colunas[0]:
        peso = st.number_input(
            "Peso (kg)",
            min_value=0.0,
            max_value=300.0,
            value=float(perfil.get("peso_kg") or 0),
            step=0.1,
        )
        idade = st.number_input(
            "Idade",
            min_value=0,
            max_value=120,
            value=int(perfil.get("idade") or 0),
            step=1,
        )
        objetivos = st.text_area(
            "Objetivos",
            value=perfil.get("objetivos", ""),
            placeholder="Ex.: melhorar 10 km e manter consistência.",
        )
    with perfil_colunas[1]:
        lesoes = st.text_area(
            "Histórico de lesões",
            value=perfil.get("historico_lesoes", ""),
            placeholder="Indica lesões relevantes, datas e limitações.",
        )
        preferencias = st.text_area(
            "Preferências de treino e feedback",
            value=perfil.get("preferencias", ""),
            placeholder="Ex.: prefere feedback direto e crítico.",
        )
    guardar_perfil = st.form_submit_button("Guardar perfil completo")

if guardar_perfil:
    dados_pessoais = {
        "peso_kg": peso or None,
        "idade": idade or None,
        "objetivos": objetivos.strip(),
        "historico_lesoes": lesoes.strip(),
        "preferencias": preferencias.strip(),
    }
    perfil_guardado = client.guardar_dados_pessoais(dados_pessoais)
    st.session_state["perfil_atleta"] = perfil_guardado
    st.success("Perfil completo guardado.")
