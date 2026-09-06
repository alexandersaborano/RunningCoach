import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from backup_data import (
    backup_automatico_devido,
    carregar_configuracao,
    criar_backup,
    guardar_configuracao,
    listar_backups,
    restaurar_backup,
    verificar_integridade,
)

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
st.code(
    "AGENT_CARGA_PROVIDER=gemini\n"
    "AGENT_FISIOLOGIA_PROVIDER=gemini\n"
    "AGENT_TREINO_PROVIDER=openai\n"
    "AGENT_CRITICO_PROVIDER=anthropic",
    language="dotenv",
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

st.subheader("Segurança dos dados locais")
try:
    backup_config = carregar_configuracao()
except ValueError as error:
    st.error(str(error))
    backup_config = {"automatico": False, "intervalo_horas": 24, "retencao": 10, "destino": "backups"}

with st.form("configuracao_backups"):
    destino = st.text_input("Pasta de destino dos backups", value=backup_config.get("destino", "backups"))
    automatico = st.checkbox("Criar backup automático ao abrir a aplicação", value=bool(backup_config.get("automatico")))
    intervalo = st.number_input("Intervalo mínimo (horas)", min_value=1, max_value=720, value=int(backup_config.get("intervalo_horas", 24)))
    retencao = st.number_input("Número de backups a manter", min_value=1, max_value=100, value=int(backup_config.get("retencao", 10)))
    guardar_backup_config = st.form_submit_button("Guardar configuração de backups")

if guardar_backup_config:
    guardar_configuracao({
        "destino": destino.strip() or "backups",
        "automatico": automatico,
        "intervalo_horas": int(intervalo),
        "retencao": int(retencao),
    })
    st.success("Configuração de backups guardada.")
    st.rerun()

if backup_automatico_devido(backup_config):
    try:
        caminho = criar_backup(backup_config.get("destino"), int(backup_config.get("retencao", 10)))
    except (FileNotFoundError, OSError, ValueError) as error:
        st.error(f"Não foi possível criar o backup automático: {error}")
    else:
        st.info(f"Backup automático criado: {caminho.name}")

st.caption("Backups disponíveis")
backups = listar_backups(backup_config.get("destino"))
if backups:
    nomes_backups = [str(caminho) for caminho in backups]
    backup_selecionado = st.selectbox("Selecionar backup", nomes_backups)
    confirmar_restauro = st.checkbox("Confirmo que quero substituir os dados atuais.")
    if st.button("Restaurar backup selecionado", disabled=not confirmar_restauro):
        try:
            criar_backup(backup_config.get("destino"), int(backup_config.get("retencao", 10)))
            restaurar_backup(backup_selecionado)
        except (FileNotFoundError, OSError, ValueError) as error:
            st.error(f"Restauro falhou: {error}")
        else:
            st.success("Backup restaurado. Reinicia a aplicação para atualizar todos os dados.")
else:
    st.info("Ainda não existem backups na pasta configurada.")

st.subheader("Integridade dos ficheiros JSON")
problemas = verificar_integridade()
if problemas:
    st.error(f"Foram encontrados {len(problemas)} problema(s).")
    for problema in problemas:
        st.write(f"- {problema}")
else:
    st.success("Todos os ficheiros JSON locais são válidos.")
