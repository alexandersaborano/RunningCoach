import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd

from config.settings import FICHEIRO_PERFIL
from core.ai_coach import AICoach
from core.ai_evolution import (
    avaliar_resultado_recomendacao,
    calcular_sinais_fadiga,
    resumir_semana,
    selecionar_provider,
)
from core.memory_manager import MemoryManager
from ui.theme import aplicar_tema, cabecalho, navegacao
from ui.table_actions import tabela_com_acoes


st.set_page_config(page_title="Evolução AI", page_icon="🤖", layout="wide")
aplicar_tema()
navegacao()
cabecalho(
    "Evolução AI",
    "Transforma o histórico em evidência, recomendações e aprendizagem verificável.",
    "Atleta AI Coach · Inteligência",
)

memory = MemoryManager()
sessoes = memory.carregar_historico_sessoes()
recuperacao = memory.carregar_recuperacao()
coach = AICoach(memory_manager=memory)

if not sessoes:
    st.info("Guarda ou importa sessões antes de gerar uma evolução semanal.")
    st.stop()

datas = sorted(str(sessao.get("data", ""))[:10] for sessao in sessoes if sessao.get("data"))
ultima_data = date.fromisoformat(datas[-1]) if datas else date.today()
colunas = st.columns(3)
with colunas[0]:
    referencia = st.date_input("Semana de referência", value=ultima_data)
with colunas[1]:
    provider_nomes = []
    for nome in ("gemini", "openai", "anthropic"):
        provider, _ = selecionar_provider(coach.agent_registry, nome, ())
        if provider is not None:
            provider_nomes.append(nome)
    provider_escolhido = st.selectbox(
        "Provider desta análise",
        provider_nomes or ["gemini"],
        disabled=not bool(provider_nomes),
    )
with colunas[2]:
    st.metric("Sessões guardadas", len(sessoes))

inicio = referencia - timedelta(days=referencia.weekday())
resumo = resumir_semana(sessoes, recuperacao, inicio)
sinais = calcular_sinais_fadiga(sessoes, recuperacao, referencia)

st.subheader("Evidência da semana")
metricas = st.columns(5)
metricas[0].metric("Sessões", resumo["sessoes"])
metricas[1].metric("Distância", f"{resumo['distancia_km']:.1f} km")
metricas[2].metric("Carga", f"{resumo['carga_tss']:.0f} TSS")
metricas[3].metric("Pace médio", resumo["pace_medio_min_km"] or "—")
metricas[4].metric("Risco de fadiga", sinais["nivel"].title())
if sinais["sinais"]:
    for sinal in sinais["sinais"]:
        st.warning(
            f"{sinal['tipo'].replace('_', ' ').title()}: "
            f"{sinal['valor']} ({sinal['gravidade']})."
        )
else:
    st.success("Não foram detetados sinais objetivos relevantes nesta semana.")
if resumo["evidencia"]["limitacoes"]:
    st.info("Limitações: " + ", ".join(resumo["evidencia"]["limitacoes"]))

if st.button(
    "🤖 Gerar resumo semanal e recomendações",
    type="primary",
    disabled=not provider_nomes,
):
    provider, nome_provider = selecionar_provider(
        coach.agent_registry, provider_escolhido, ("gemini",)
    )
    if provider is None:
        st.error("O provider selecionado não está configurado.")
    else:
        perfil = {}
        if FICHEIRO_PERFIL.exists():
            import json
            perfil = json.loads(FICHEIRO_PERFIL.read_text(encoding="utf-8"))
        prompt = f"""És um treinador de corrida. Produz um resumo semanal em Português.
Usa apenas a evidência fornecida, identifica limitações e termina com uma secção
RECOMENDAÇÕES PARA A PRÓXIMA SEMANA. Não faças diagnóstico médico.

PERFIL:
{perfil or "Não preenchido"}

RESUMO OBJETIVO:
{resumo}

SINAIS DE CARGA E RECUPERAÇÃO:
{sinais}
"""
        try:
            resposta = provider.generate(prompt)
        except Exception as error:
            st.error(f"Não foi possível gerar o resumo: {error}")
        else:
            resumo_guardado = {
                **resumo,
                "sinais_fadiga": sinais,
                "provider": nome_provider,
                "resposta": resposta,
                "gerado_em": date.today().isoformat(),
            }
            memory.guardar_resumo_semanal(resumo_guardado)
            st.session_state["resumo_ai_atual"] = resumo_guardado
            st.success("Resumo semanal guardado.")

atual = st.session_state.get("resumo_ai_atual")
if atual:
    st.subheader("Resumo e recomendações")
    st.caption(f"Provider: {atual.get('provider')} · Semana: {atual.get('semana_inicio')}")
    st.markdown(atual.get("resposta", "Sem resposta."))

    st.subheader("Avaliar recomendação")
    with st.form("avaliar_recomendacao"):
        recomendacao = st.text_area("Recomendação a avaliar", value=atual.get("resposta", ""))
        resultado = st.selectbox(
            "Resultado observado",
            ["favoravel", "parcial", "desfavoravel", "sem_evidencia"],
        )
        feedback = st.text_area("Feedback do atleta (opcional)")
        guardar_resultado = st.form_submit_button("Guardar avaliação")
    if guardar_resultado:
        avaliacao = avaliar_resultado_recomendacao(
            recomendacao,
            [{"executada": resultado == "favoravel"}] if resultado != "sem_evidencia" else [],
            feedback,
        )
        avaliacao["resultado_declarado"] = resultado
        avaliacao["semana_inicio"] = atual.get("semana_inicio")
        memory.guardar_resultado_recomendacao(avaliacao)
        st.success("Avaliação guardada para aprendizagem futura.")

st.subheader("Histórico de evolução AI")
for item in reversed(memory.carregar_resumos_semanais()[-8:]):
    with st.expander(
        f"{item.get('semana_inicio', 'sem data')} · {item.get('provider', 'desconhecido')}"
    ):
        st.markdown(item.get("resposta", "Sem resposta guardada."))

avaliacoes = memory.carregar_resultados_recomendacoes()
if avaliacoes:
    st.subheader("Avaliações guardadas")
    tabela_com_acoes(
        pd.DataFrame(avaliacoes),
        key="evolucao_avaliacoes",
        file_stem="avaliacoes_recomendacoes",
    )
