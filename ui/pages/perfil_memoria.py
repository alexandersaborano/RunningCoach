import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

from core.intervals_client import IntervalsClient
from core.heart_rate_zones import calcular_zonas_hrr
from core.memory_manager import MemoryManager
from ui.theme import aplicar_tema, cabecalho, navegacao


st.set_page_config(page_title="Perfil do atleta", page_icon="👤", layout="wide")
aplicar_tema()
navegacao()

client = IntervalsClient()
memory = MemoryManager()

cabecalho(
    "Perfil do atleta",
    "Uma visão completa das métricas, objetivos e contexto que orientam o treinador.",
    "Atleta AI Coach · Identidade",
)

if client.api_key and str(client.athlete_id) != "0":
    atleta_url = f"https://intervals.icu/athlete/{client.athlete_id}"
    col_links = st.columns([1, 1, 2])
    with col_links[0]:
        st.link_button("🌐 Abrir no Intervals.icu", atleta_url, use_container_width=True)
    with col_links[1]:
        if st.button("🔄 Sincronizar Tudo", use_container_width=True):
            with st.spinner("A sincronizar dados..."):
                perfil_atualizado = client.obter_perfil_e_zonas()
                if perfil_atualizado:
                    st.session_state["perfil_atleta"] = perfil_atualizado
                wellness_inicio = (date.today() - timedelta(days=30)).isoformat()
                wellness_fim = date.today().isoformat()
                wellness_remoto = client.obter_bem_estar(wellness_inicio, wellness_fim)
                if wellness_remoto:
                    memory.sincronizar_bem_estar(wellness_remoto)
                st.success("Dados sincronizados com o Intervals.icu!")
                st.rerun()

wellness = memory.carregar_recuperacao()
if wellness:
    registros = sorted(
        (item for item in wellness.values() if isinstance(item, dict)),
        key=lambda item: str(item.get("data", "")),
        reverse=True,
    )
    ultimo = registros[0] if registros else {}
    if ultimo:
        st.subheader("🩺 Wellness sincronizado")
        data_reg = ultimo.get("data", "")
        sinc_em = ultimo.get("sincronizado_em", "")
        st.caption(
            f"Último registo: **{data_reg}**"
            + (f" · Sincronizado: {sinc_em[:16].replace('T', ' ')}" if sinc_em else "")
        )
        colunas = st.columns(4)
        colunas[0].metric("Sono", f"{float(ultimo.get('sono_horas', 0) or 0):.1f} h")
        colunas[1].metric("Recuperação", f"{float(ultimo.get('recuperacao', 0) or 0):.0f}/10")
        colunas[2].metric("FC Repouso", f"{float(ultimo.get('fc_repouso', 0) or 0):.0f} bpm")
        hrv_val = ultimo.get("hrv")
        colunas[3].metric("HRV (SDNN/rMSSD)", f"{float(hrv_val):.0f} ms" if hrv_val is not None else "--")


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
        st.caption(
            "Fórmula: FC repouso + (%HRR × (FC máxima - FC repouso)). "
            f"Valores usados: FC repouso {perfil.get('resting_hr')} bpm e "
            f"FC máxima {perfil.get('max_hr')} bpm."
        )
        percentagens_hrr = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
        limites_hrr = [round(perfil["resting_hr"])]
        limites_hrr.extend(zonas_hrr)
        st.write("Zonas calculadas por %HRR (Karvonen):")
        for indice in range(5):
            st.write(
                f"Z{indice + 1}: {percentagens_hrr[indice] * 100:.0f}-"
                f"{percentagens_hrr[indice + 1] * 100:.0f}% HRR · "
                f"{limites_hrr[indice]}-{limites_hrr[indice + 1]} bpm"
            )
    perfis_zonas = perfil.get("perfis_zonas", {})
    if perfis_zonas:
        nomes_perfis = list(perfis_zonas)
        ativo = perfil.get("perfil_zonas_ativo", nomes_perfis[0])
        if ativo not in nomes_perfis:
            ativo = nomes_perfis[0]
        selecionado = st.selectbox(
            "Perfil de zonas ativo",
            nomes_perfis,
            index=nomes_perfis.index(ativo),
            key="perfil_zonas_ativo",
        )
        if st.button("Guardar perfil de zonas ativo"):
            perfil_guardado = client.guardar_perfil_zonas_ativo(selecionado)
            st.session_state["perfil_atleta"] = perfil_guardado
            st.success(f"Perfil de zonas ativo: {selecionado}.")
            st.rerun()
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
