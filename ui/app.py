import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
from config.settings import HISTORICO_DIR
from core.intervals_client import IntervalsClient
from core.memory_manager import MemoryManager
from core.ai_coach import AICoach
from core.training_comparison import construir_comparacao
from ui.theme import aplicar_tema, cabecalho, navegacao
from ui.table_actions import tabela_com_acoes

st.set_page_config(
    page_title="Sessões | Atleta AI Coach",
    page_icon="🏃",
    layout="wide"
)
aplicar_tema()
navegacao()

client = IntervalsClient()
memory = MemoryManager()
coach = AICoach(memory_manager=memory)
if not coach.disponivel:
    st.warning(f"Análise AI indisponível: {coach.config_error}")

# ==============================================================================
# BARRA LATERAL (SIDEBAR)
# ==============================================================================
st.sidebar.subheader("⚙️ Estado atual")
perfil = client.obter_perfil_e_zonas()
data_recuperacao = date.today().isoformat()
recuperacao_guardada = memory.carregar_recuperacao(data_recuperacao)
sono_horas = float(recuperacao_guardada.get("sono_horas", 8.0))
recuperacao = int(recuperacao_guardada.get("recuperacao", 7))
fc_repouso_atual = int(
    recuperacao_guardada.get("fc_repouso", (perfil or {}).get("resting_hr") or 0)
)

if perfil:
    st.sidebar.success("Zonas de FC Carregadas")
    st.sidebar.metric("FC Máxima", f"{perfil.get('max_hr', '--')} bpm")
    st.sidebar.metric("Limiar (LTHR)", f"{perfil.get('lthr', '--')} bpm")
    st.sidebar.metric("FC Repouso", f"{perfil.get('resting_hr', '--')} bpm")
    
    with st.sidebar.expander("Ver Limites de Zonas"):
        for idx, z in enumerate(perfil.get("zonas_hr", []), 1):
            st.write(f"**Zona {idx}:** {z} bpm")
    with st.sidebar.expander("🩺 Dados de recuperação"):
        sono_horas = st.number_input(
            "Sono na última noite (horas)",
            min_value=0.0,
            max_value=24.0,
            value=st.session_state.get("sono_horas", 8.0),
            step=0.5,
            key="sono_horas",
        )
        recuperacao = st.slider(
            "Recuperação percebida (1-10)",
            min_value=1,
            max_value=10,
            value=st.session_state.get("recuperacao", 7),
            key="recuperacao",
        )
        fc_repouso_atual = st.number_input(
            "FC de repouso atual (bpm)",
            min_value=0,
            max_value=250,
            value=int(perfil.get("resting_hr") or 0),
            step=1,
            key="fc_repouso_atual",
        )
        if st.button("💾 Guardar recuperação de hoje", key="guardar_recuperacao"):
            memory.guardar_recuperacao(
                data_recuperacao,
                sono_horas,
                recuperacao,
                fc_repouso_atual,
            )
            st.success("Dados de recuperação guardados.")
else:
    st.sidebar.error("Zonas de FC não detetadas no Intervals.icu")

st.sidebar.markdown("---")
st.sidebar.subheader("🧠 Memória Adaptativa")

memoria_data = memory.carregar_memoria()
padroes = memoria_data.get("padroes_atleta", [])
regras = memoria_data.get("regras_estilo", [])

with st.sidebar.expander(f"Padrões Registados ({len(padroes)})"):
    for p in padroes:
        st.markdown(f"- {p}")

with st.sidebar.expander(f"Regras de Estilo ({len(regras)})"):
    for r in regras:
        st.markdown(f"- {r}")

historico = memory.carregar_historico_sessoes()
if historico:
    st.sidebar.metric("Sessões no histórico", len(historico))

# ==============================================================================
# ÁREA PRINCIPAL
# ==============================================================================
cabecalho(
    "Centro de performance",
    "Transforma cada sessão em decisões melhores para a próxima semana.",
    "Atleta AI Coach · Sessões",
)

if historico:
    st.subheader("📈 Evolução do atleta")
    historico_df = pd.DataFrame([
        {
            "atividade_id": sessao.get("atividade_id"),
            "Data": sessao.get("data", "")[:10],
            "Nome": sessao.get("nome", "Sem nome"),
            "Tipo": sessao.get("tipo", "Desconhecido"),
            "Distância (km)": sessao.get("distancia_km", 0),
            "Pace (min/km)": sessao.get("pace_min_km"),
            "FC média (bpm)": sessao.get("fc_media"),
            "Carga (TSS)": sessao.get("carga_tss", 0),
        }
        for sessao in historico
    ])
    historico_df["Data"] = pd.to_datetime(historico_df["Data"], errors="coerce")
    historico_df = historico_df.dropna(subset=["Data"])
    if not historico_df.empty:
        def reset_historico_filtros():
            for chave in ("historico_periodo", "historico_tipo", "historico_distancia"):
                st.session_state.pop(chave, None)

        st.button(
            "↺ Reset aos filtros",
            key="reset_graficos",
            on_click=reset_historico_filtros,
        )
        filtro_colunas = st.columns(3)
        data_min = historico_df["Data"].min().date()
        data_max = historico_df["Data"].max().date()
        with filtro_colunas[0]:
            periodo = st.date_input(
                "Período do histórico",
                value=(data_min, data_max),
                min_value=data_min,
                max_value=data_max,
                key="historico_periodo",
            )
        with filtro_colunas[1]:
            tipos = ["Todos"] + sorted(historico_df["Tipo"].fillna("Desconhecido").unique())
            tipo_selecionado = st.selectbox("Tipo de treino", tipos, key="historico_tipo")
        with filtro_colunas[2]:
            distancia_min = float(historico_df["Distância (km)"].min())
            distancia_max = float(historico_df["Distância (km)"].max())
            if distancia_min == distancia_max:
                st.caption(f"Distância: {distancia_min:.2f} km")
                distancia = (distancia_min, distancia_max)
            else:
                distancia = st.slider(
                    "Distância (km)",
                    min_value=distancia_min,
                    max_value=distancia_max,
                    value=(distancia_min, distancia_max),
                    key="historico_distancia",
                )
        if isinstance(periodo, tuple) and len(periodo) == 2:
            historico_filtrado = historico_df[
                (historico_df["Data"].dt.date >= periodo[0])
                & (historico_df["Data"].dt.date <= periodo[1])
            ]
        else:
            historico_filtrado = historico_df
        historico_filtrado = historico_filtrado[
            historico_filtrado["Distância (km)"].between(distancia[0], distancia[1])
        ]
        if tipo_selecionado != "Todos":
            historico_filtrado = historico_filtrado[
                historico_filtrado["Tipo"] == tipo_selecionado
            ]

        if historico_filtrado.empty:
            st.info("Nenhuma sessão corresponde aos filtros selecionados.")
        else:
            evolucao = historico_filtrado.sort_values("Data").set_index("Data")
            fig = go.Figure()
            for coluna in ["Distância (km)", "FC média (bpm)", "Carga (TSS)"]:
                fig.add_trace(go.Scatter(
                    x=evolucao.index, y=evolucao[coluna], mode="lines+markers", name=coluna
                ))
            fig.update_layout(
                title="Distância, frequência cardíaca e carga",
                xaxis_title="Data",
                yaxis_title="Valor",
                uirevision=st.session_state.get("graficos_reset", 0),
            )
            st.plotly_chart(
                fig,
                width="stretch",
                key=f"grafico_metricas_{st.session_state.get('graficos_reset', 0)}",
            )
            pace_evolucao = evolucao[["Pace (min/km)"]].dropna()
            if not pace_evolucao.empty:
                pace_fig = go.Figure(go.Scatter(
                    x=pace_evolucao.index,
                    y=pace_evolucao["Pace (min/km)"],
                    mode="lines+markers",
                    name="Pace",
                ))
                pace_fig.update_layout(
                    title="Evolução do pace",
                    xaxis_title="Data",
                    yaxis_title="Minutos por km",
                    yaxis_autorange="reversed",
                    uirevision=st.session_state.get("graficos_reset", 0),
                )
                st.plotly_chart(
                    pace_fig,
                    width="stretch",
                    key=f"grafico_pace_{st.session_state.get('graficos_reset', 0)}",
                )

            historico_filtrado["Semana"] = historico_filtrado["Data"].dt.to_period("W").astype(str)
            semanal = historico_filtrado.groupby("Semana").agg(
                Distância_km=("Distância (km)", "sum"),
                Carga_TSS=("Carga (TSS)", "sum"),
                Sessões=("Nome", "count"),
            )
            mensal = historico_filtrado.assign(
                Mês=historico_filtrado["Data"].dt.to_period("M").astype(str)
            ).groupby("Mês").agg(
                Distância_km=("Distância (km)", "sum"),
                Carga_TSS=("Carga (TSS)", "sum"),
                Sessões=("Nome", "count"),
            )
            st.subheader("📊 Resumo semanal e mensal")
            resumo_colunas = st.columns(2)
            with resumo_colunas[0]:
                st.caption("Semanal")
                tabela_com_acoes(
                    semanal.reset_index(),
                    key="historico_semanal",
                    file_stem="historico_semanal",
                )
            with resumo_colunas[1]:
                st.caption("Mensal")
                tabela_com_acoes(
                    mensal.reset_index(),
                    key="historico_mensal",
                    file_stem="historico_mensal",
                )

            ultimos_7 = historico_df[
                historico_df["Data"] >= historico_df["Data"].max() - pd.Timedelta(days=7)
            ]["Carga (TSS)"].sum()
            ultimos_28 = historico_df[
                historico_df["Data"] >= historico_df["Data"].max() - pd.Timedelta(days=28)
            ]["Carga (TSS)"].sum()
            ratio_carga = ultimos_7 / (ultimos_28 / 4) if ultimos_28 > 0 else 0
            st.subheader("🩺 Indicador de fadiga e carga")
            baseline_fc = float(perfil.get("resting_hr") or 0) if perfil else 0
            desvio_fc = (
                (fc_repouso_atual - baseline_fc) / baseline_fc
                if baseline_fc > 0 and fc_repouso_atual > 0 else 0
            )
            sinais_fadiga = []
            if ratio_carga > 1.3:
                sinais_fadiga.append("carga aguda elevada")
            if sono_horas < 7:
                sinais_fadiga.append("sono reduzido")
            if recuperacao <= 4:
                sinais_fadiga.append("recuperação percebida baixa")
            if desvio_fc > 0.08:
                sinais_fadiga.append("FC de repouso acima do habitual")
            score_fadiga = len(sinais_fadiga)
            if score_fadiga >= 2:
                st.warning(
                    "Sinais combinados de fadiga: "
                    + ", ".join(sinais_fadiga)
                    + ". Considera reduzir a intensidade."
                )
            elif score_fadiga == 1:
                st.info("Sinal de atenção: " + sinais_fadiga[0] + ". Monitoriza a recuperação.")
            elif ratio_carga > 0:
                st.success("Carga e recuperação sem sinais relevantes de fadiga.")
            else:
                st.info("Ainda não há carga TSS suficiente para estimar fadiga.")
            exportar = historico_filtrado.drop(columns=["Semana"], errors="ignore").copy()
            exportar["Data"] = exportar["Data"].dt.strftime("%Y-%m-%d")
            tabela_com_acoes(
                exportar,
                key="historico_tabela",
                file_stem="historico_atleta",
                title="Tabela de sessões filtradas",
            )

        if st.button(
            "🧠 Analisar evolução global com Gemini",
            type="primary",
            disabled=not coach.disponivel,
        ):
            with st.spinner("A analisar o histórico relevante..."):
                ids_relevantes = set(historico_filtrado["atividade_id"])
                sessoes_relevantes = [
                    sessao for sessao in historico
                    if sessao.get("atividade_id") in ids_relevantes
                ]
                recuperacao_historico = memory.carregar_recuperacao()
                analises_anteriores = memory.carregar_analises_globais()
                analise_global = coach.analisar_historico_multiagente(
                    sessoes_relevantes,
                    recuperacao_por_data=recuperacao_historico,
                    analises_anteriores=analises_anteriores,
                    perfil=perfil,
                )
                contexto_global = {
                    "data": datetime.now().isoformat(timespec="seconds"),
                    "filtros": {
                        "periodo": [str(valor) for valor in periodo]
                        if isinstance(periodo, tuple) else str(periodo),
                        "tipo": tipo_selecionado,
                        "distancia_km": list(distancia),
                    },
                    "atividade_ids": [
                        sessao.get("atividade_id") for sessao in sessoes_relevantes
                    ],
                    "sessoes": sessoes_relevantes,
                    "recuperacao": recuperacao_historico,
                    "analise": analise_global,
                }
                memory.guardar_analise_global(contexto_global)
                st.session_state["analise_global"] = analise_global
        if st.session_state.get("analise_global"):
            st.subheader("🧭 Plano de evolução progressiva")
            st.markdown(st.session_state["analise_global"])

col_d1, col_d2 = st.columns(2)
with col_d1:
    data_inicio = st.date_input("Data Inicial", pd.to_datetime("2026-08-01"))
with col_d2:
    data_fim = st.date_input("Data Final", pd.to_datetime("today"))

str_inicio = data_inicio.strftime("%Y-%m-%d")
str_fim = data_fim.strftime("%Y-%m-%d")

def atividade_para_historico(corrida: dict) -> dict:
    distancia_km = round((corrida.get("distance") or 0) / 1000, 2)
    moving_time = corrida.get("moving_time") or 0
    return {
        "atividade_id": corrida.get("id"),
        "data": corrida.get("start_date_local", datetime.now().isoformat()),
        "nome": corrida.get("name", "Sem nome"),
        "tipo": corrida.get("type") or corrida.get("icu_type", "Desconhecido"),
        "distancia_km": distancia_km,
        "tempo_movimento_min": round(moving_time / 60, 2),
        "pace_min_km": round((moving_time / 60) / distancia_km, 2) if distancia_km else None,
        "fc_media": corrida.get("average_heartrate"),
        "fc_maxima": corrida.get("max_heartrate"),
        "carga_tss": corrida.get("icu_training_load") or 0,
    }

if st.button("⬇️ Importar histórico antigo do Intervals.icu"):
    with st.spinner("A importar sessões antigas..."):
        corridas_importadas = client.obter_corridas(str_inicio, str_fim)
        ids_existentes = memory.ids_sessoes_existentes()
        sessoes = [
            atividade_para_historico(corrida)
            for corrida in (corridas_importadas or [])
            if corrida.get("id") and str(corrida["id"]) not in ids_existentes
        ]
        quantidade = memory.guardar_sessoes_importadas(sessoes)
        total_encontrado = len(corridas_importadas or [])
        ignoradas = total_encontrado - len(sessoes)
        st.success(
            f"{quantidade} sessão(ões) nova(s) importada(s); "
            f"{ignoradas} já existente(s) ignorada(s)."
        )
        if quantidade:
            st.rerun()

if st.button("🔎 Procurar Corridas no Intervals.icu", type="primary"):
    with st.spinner(f"A consultar Intervals.icu entre {str_inicio} e {str_fim}..."):
        resultados = client.obter_corridas(str_inicio, str_fim)
        if resultados:
            st.session_state["corridas"] = resultados
            st.session_state["pesquisa_efetuada"] = True
        else:
            st.session_state["corridas"] = []
            st.session_state["pesquisa_efetuada"] = True
            st.warning("⚠️ Nenhuma corrida encontrada no intervalo selecionado.")

if st.session_state.get("pesquisa_efetuada"):
    corridas = st.session_state.get("corridas", [])
    
    if not corridas:
        st.info("ℹ️ Tenta alargar o intervalo de datas acima para encontrar sessões gravadas.")
    else:
        st.success(f"{len(corridas)} corrida(s) encontrada(s) no período.")
        
        opcoes_corridas = {}
        for idx, c in enumerate(corridas):
            data_str = c.get('start_date_local', 'Data Desconhecida')[:10]
            nome = c.get('name', 'Sem Nome')
            dist = round((c.get('distance') or 0) / 1000, 2)
            label = f"{data_str} | {nome} ({dist} km)"
            opcoes_corridas[label] = idx
        
        sessao_selecionada = st.selectbox("Selecione a sessão a analisar:", list(opcoes_corridas.keys()))
        idx_corrida = opcoes_corridas[sessao_selecionada]
        corrida = corridas[idx_corrida]
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Distância", f"{round((corrida.get('distance') or 0)/1000, 2)} km")
        m2.metric("Tempo Em Movimento", f"{round((corrida.get('moving_time') or 0)/60, 1)} min")
        m3.metric("FC Média", f"{round(corrida.get('average_heartrate') or 0)} bpm")
        m4.metric("FC Máxima", f"{round(corrida.get('max_heartrate') or 0)} bpm")
        m5.metric("Carga (TSS)", corrida.get("icu_training_load") or 0)

        # Obter laps/intervalos da sessão
        laps = client.obter_laps_atividade(corrida.get("id"))
        
        if not laps:
            st.warning("⚠️ A API do Intervals.icu não devolveu laps/intervalos individuais para esta atividade. A exibir resumo global.")
            laps = [{
                "distance": corrida.get("distance", 0),
                "elapsed_time": corrida.get("elapsed_time") or corrida.get("moving_time", 0),
                "moving_time": corrida.get("moving_time", 0),
                "average_heartrate": corrida.get("average_heartrate", 0),
                "max_heartrate": corrida.get("max_heartrate", 0),
                "label": "Treino Total"
            }]

        st.subheader("⏱️ Métricas por Lap / Intervalo")
        laps_data = []
        laps_txt_list = []
        
        for idx, lap in enumerate(laps, start=1):
            dist_m = lap.get("distance", 0)
            dist_km = round(dist_m / 1000.0, 2) if dist_m else 0
            
            elapsed_sec = lap.get("elapsed_time", lap.get("moving_time", 0))
            mins = int(elapsed_sec // 60)
            secs = int(elapsed_sec % 60)
            tempo_str = f"{mins}m{secs:02d}s"
            
            pace_str = "N/A"
            if dist_km > 0 and elapsed_sec > 0:
                pace_sec = elapsed_sec / dist_km
                p_min = int(pace_sec // 60)
                p_sec = int(pace_sec % 60)
                pace_str = f"{p_min}:{p_sec:02d}/km"

            label = lap.get("label") or lap.get("type") or lap.get("name") or f"Lap {idx}"
            fc_avg = round(lap.get("average_heartrate") or 0)
            fc_max = round(lap.get("max_heartrate") or 0)

            laps_data.append({
                "Lap": idx,
                "Etiqueta": label,
                "Distância (km)": dist_km,
                "Tempo": tempo_str,
                "Pace": pace_str,
                "FC Média (bpm)": fc_avg,
                "FC Máx (bpm)": fc_max
            })
            laps_txt_list.append(f"Lap {idx} | {label} | {dist_km} km | {tempo_str} | {pace_str} | FC Média: {fc_avg} bpm | FC Máx: {fc_max} bpm")
        
        df_laps = pd.DataFrame(laps_data)
        tabela_com_acoes(df_laps, key="laps_tabela", file_stem="laps")
        
        zonas_str = "\n".join([f"Z{i}: {z} bpm" for i, z in enumerate(perfil.get('zonas_hr', []), 1)]) if perfil else "Zonas não disponíveis."
        descricao_plano = corrida.get("description") or corrida.get("workout_doc", {}).get("description") or "Sem prescrição."
        comparacao_treino = construir_comparacao(corrida, descricao_plano)
        
        relatorio_detalhado = f"""
DATA DA ATIVIDADE: {corrida.get('start_date_local', '')[:10]} | NOME: {corrida.get('name')}
VOLUME: {round((corrida.get('distance') or 0)/1000, 2)} km | TEMPO: {round((corrida.get('moving_time') or 0)/60, 1)} min | TSS: {corrida.get('icu_training_load')}
FC MÉDIA: {corrida.get('average_heartrate')} bpm | FC MÁXIMA: {corrida.get('max_heartrate')} bpm
--------------------------------------------------
ZONAS DE FC DO ATLETA:
{zonas_str}
--------------------------------------------------
PRESCRIÇÃO DO PLANO DE TREINO:
{descricao_plano}
--------------------------------------------------
MÉTRICAS POR LAP:
""" + "\n".join(laps_txt_list)

        st.markdown("---")
        with st.expander("📋 Comparar treino prescrito vs. realizado"):
            st.markdown("**Prescrição**")
            st.write(comparacao_treino["prescricao"])
            st.markdown("**Execução registada**")
            tabela_com_acoes(
                pd.DataFrame([comparacao_treino["realizado"]]),
                key="comparacao_treino_tabela",
                file_stem="comparacao_treino",
            )
        
        if st.button(
            "🤖 Gerar Análise com Gemini",
            type="primary",
            disabled=not coach.disponivel,
        ):
            with st.spinner("O Gemini está a analisar a sessão..."):
                analise = coach.analisar_sessao(relatorio_detalhado)
                st.session_state["ultima_analise"] = analise
                st.session_state["ultimo_relatorio"] = relatorio_detalhado
                sessao = atividade_para_historico(corrida)
                atividade_id = sessao["atividade_id"]
                if atividade_id:
                    sessao.update({
                        "analise": analise,
                        "relatorio": relatorio_detalhado,
                        "prescricao": descricao_plano,
                        "comparacao_treino": comparacao_treino,
                    })
                    memory.guardar_sessao(sessao)
                    st.success("Sessão guardada no histórico.")
                else:
                    st.warning("A sessão não tem ID e não pôde ser guardada.")

        if "ultima_analise" in st.session_state:
            st.markdown("### 📋 Relatório do Treinador AI")
            st.markdown(st.session_state["ultima_analise"])
            
            st.markdown("---")
            st.subheader("💬 Feedback e Aprendizagem Contínua")
            
            with st.form("form_feedback"):
                user_fb = st.text_input("Comentário / Ajuste ao relatório:", placeholder="Ex: O lap 3 teve FC alta porque apanhei uma subida acentuada.")
                submetido = st.form_submit_button(
                    "Enviar Feedback & Atualizar IA",
                    disabled=not coach.disponivel,
                )
                
                if submetido and user_fb:
                    with st.spinner("A processar feedback com o Gemini..."):
                        sucesso, novo_p, nova_i = coach.processar_feedback(
                            st.session_state["ultimo_relatorio"],
                            st.session_state["ultima_analise"],
                            user_fb
                        )
                        if sucesso:
                            st.success("Memória atualizada com sucesso!")
                            if novo_p:
                                st.info(f"**Novo Padrão Identificado:** {novo_p}")
                            if nova_i:
                                st.warning(f"**Nova Regra de Análise:** {nova_i}")
                            st.rerun()
                        else:
                            st.error(
                                "Não foi possível guardar o feedback. "
                                f"{coach.ultimo_erro or 'Tenta novamente.'}"
                            )