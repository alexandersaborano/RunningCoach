import json
from google import genai
from google.genai import types
from config.settings import (
    ANTHROPIC_API_KEY,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
)
from core.ai_agents import (
    AgentRegistry,
    AnthropicProvider,
    GeminiProvider,
    OpenAIProvider,
    SpecializedAgentRunner,
)


class AICoach:

    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager
        self.client = None
        self.config_error = None
        if GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except ValueError:
                self.config_error = (
                    "A configuração do Gemini foi rejeitada. "
                    "Confirma o secret GEMINI_API_KEY no Streamlit Cloud."
                )
        else:
            self.config_error = (
                "GEMINI_API_KEY não está configurada. "
                "Adiciona-a em Settings > Secrets no Streamlit Cloud."
            )
        self.model_id = "gemini-3.6-flash"
        self.chat_session = None
        self.ultimo_erro = None
        self.agent_registry = AgentRegistry()
        if self.client is not None:
            self.agent_registry.register(
                "gemini", GeminiProvider(self.client, self.model_id)
            )
        if OPENAI_API_KEY:
            self.agent_registry.register("openai", OpenAIProvider(OPENAI_API_KEY))
        if ANTHROPIC_API_KEY:
            self.agent_registry.register(
                "anthropic", AnthropicProvider(ANTHROPIC_API_KEY)
            )

    @property
    def disponivel(self) -> bool:
        return self.client is not None

    def analisar_sessao(self, relatorio_detalhado: str) -> str:
        """
        Gera o relatório de análise inicial da sessão usando generate_content
        com AFC desativado para evitar warnings.
        """
        contexto_memoria = ""
        if self.memory_manager:
            mem = self.memory_manager.carregar_memoria()
            padroes = mem.get("padroes_atleta", [])
            regras = mem.get("regras_estilo", [])
            if padroes or regras:
                contexto_memoria = f"\nPADRÕES REGISTADOS DO ATLETA:\n{padroes}\n\nREGRAS DE ANÁLISE:\n{regras}\n"

        prompt = f"""Tu és um treinador de corrida de elite. Analisa a seguinte sessão de treino e fornece um feedback construtivo, detalhado e motivador em Português.

{contexto_memoria}
DADOS DO TREINO:
{relatorio_detalhado}

COMPARAÇÃO OBRIGATÓRIA:
Compara a prescrição do plano com a execução real. Identifica o que foi cumprido,
desvios de distância, duração, intensidade, zonas de FC, laps/intervalos e carga.
Se a prescrição não tiver dados mensuráveis, declara essa limitação explicitamente.
"""
        try:
            # Configuração stateless sem AFC para a geração inicial
            config = types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config
            )
            
            # Inicializa uma sessão de Chat para interações seguintes contínuas
            self.chat_session = self.client.chats.create(model=self.model_id)

            return response.text
        except Exception as e:
            return f"Erro ao comunicar com o Gemini: {e}"

    def analisar_historico_global(
        self,
        sessoes: list,
        recuperacao_por_data: dict = None,
        analises_anteriores: list = None,
        perfil: dict = None,
    ) -> str:
        """Analisa tendências do histórico relevante para orientar progressão."""
        if not sessoes:
            return "Não existem sessões suficientes para uma análise global."
        recuperacao_por_data = recuperacao_por_data or {}
        analises_anteriores = analises_anteriores or []
        perfil = perfil or {}
        referencia = "\n\n".join(
            f"ANÁLISE ANTERIOR {idx + 1} ({item.get('data', 'sem data')}):\n"
            f"{item.get('analise', '')}"
            for idx, item in enumerate(analises_anteriores[-3:])
        )
        resumo = "\n".join(
            f"- {s.get('data', '')[:10]} | {s.get('nome', 'Sem nome')} | "
            f"{s.get('distancia_km', 0)} km | pace {s.get('pace_min_km', 'N/A')} | "
            f"FC média {s.get('fc_media', 'N/A')} | TSS {s.get('carga_tss', 0)} | "
            f"prescrição: {s.get('prescricao', 'N/A')} | "
            f"comparação: {s.get('comparacao_treino', 'N/A')} | "
            f"sono {recuperacao_por_data.get(s.get('data', '')[:10], {}).get('sono_horas', 'N/A')} h | "
            f"recuperação {recuperacao_por_data.get(s.get('data', '')[:10], {}).get('recuperacao', 'N/A')}/10 | "
            f"FC repouso {recuperacao_por_data.get(s.get('data', '')[:10], {}).get('fc_repouso', 'N/A')} bpm"
            for s in sessoes[-60:]
        )
        analises_individuais = "\n\n".join(
            f"ANÁLISE INDIVIDUAL {idx + 1} ({s.get('data', '')[:10]} | "
            f"{s.get('nome', 'Sem nome')}):\n{s.get('analise', '')}"
            for idx, s in enumerate(sessoes[-20:])
            if s.get("analise")
        )
        if len(analises_individuais) > 30000:
            analises_individuais = analises_individuais[-30000:]
        prompt = f"""És o agente coordenador de um sistema de treino multiagente.
Analisa a evolução do atleta com base nas sessões e nos dados de recuperação abaixo.
Considera volume, pace, frequência cardíaca, carga, consistência, sono,
recuperação percebida, FC de repouso e sinais de fadiga. Relaciona alterações
de desempenho com recuperação quando existirem dados. Identifica progressos,
limitações e propõe uma progressão realista para as próximas semanas. Sê crítico,
não inventes dados e responde em Português.

PERFIL E OBJETIVOS DO ATLETA:
{perfil or "Perfil não preenchido."}

SESSÕES RELEVANTES:
{resumo}

ANÁLISES INDIVIDUAIS RELEVANTES:
{analises_individuais or "Nenhuma análise individual disponível."}

ANÁLISES GLOBAIS ANTERIORES (usa apenas para comparar evolução e corrigir conclusões):
{referencia or "Nenhuma análise anterior disponível."}
"""
        try:
            self.ultimo_erro = None
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                ),
            )
            return response.text
        except Exception as e:
            self.ultimo_erro = str(e)
            return f"Erro ao analisar o histórico: {e}"

    def analisar_historico_multiagente(
        self,
        sessoes: list,
        recuperacao_por_data: dict = None,
        analises_anteriores: list = None,
        perfil: dict = None,
    ) -> str:
        """Executa agentes especializados e o coordenador Gemini."""
        contexto = self._construir_contexto_global(
            sessoes, recuperacao_por_data, analises_anteriores, perfil
        )
        try:
            self.ultimo_erro = None
            return SpecializedAgentRunner(self.agent_registry).run(contexto)
        except Exception as error:
            self.ultimo_erro = str(error)
            return f"Erro na análise multiagente: {error}"

    def _construir_contexto_global(
        self,
        sessoes: list,
        recuperacao_por_data=None,
        analises_anteriores=None,
        perfil=None,
    ) -> str:
        """Constrói contexto partilhado pelos agentes especializados."""
        if not sessoes:
            return "Não existem sessões suficientes."
        recuperacao_por_data = recuperacao_por_data or {}
        perfil = perfil or {}
        linhas = []
        for sessao in sessoes[-60:]:
            data = sessao.get("data", "")[:10]
            recuperacao = recuperacao_por_data.get(data, {})
            linhas.append(
                f"- {data} | {sessao.get('nome', 'Sem nome')} | "
                f"{sessao.get('distancia_km', 0)} km | pace {sessao.get('pace_min_km', 'N/A')} | "
                f"FC {sessao.get('fc_media', 'N/A')} | TSS {sessao.get('carga_tss', 0)} | "
                f"prescrição {sessao.get('prescricao', 'N/A')} | "
                f"comparação {sessao.get('comparacao_treino', 'N/A')} | "
                f"sono {recuperacao.get('sono_horas', 'N/A')} h | "
                f"recuperação {recuperacao.get('recuperacao', 'N/A')}/10 | "
                f"FC repouso {recuperacao.get('fc_repouso', 'N/A')}"
            )
        anteriores = "\n".join(
            item.get("analise", "") for item in (analises_anteriores or [])[-2:]
        )
        individuais = "\n\n".join(
            sessao.get("analise", "") for sessao in sessoes[-10:] if sessao.get("analise")
        )
        return (
            "PERFIL E OBJETIVOS DO ATLETA:\n" + (str(perfil) if perfil else "Não preenchido.")
            + "\n\nSESSÕES:\n" + "\n".join(linhas)
            + "\n\nANÁLISES INDIVIDUAIS:\n" + (individuais or "Nenhuma")
            + "\n\nANÁLISES GLOBAIS ANTERIORES:\n" + (anteriores or "Nenhuma")
        )

    def enviar_mensagem_chat(self, mensagem_usuario: str) -> str:
        """
        Permite ao atleta interagir continuamente com o treinador usando a API de Chat.
        """
        if not self.chat_session:
            self.chat_session = self.client.chats.create(model=self.model_id)
        
        try:
            response = self.chat_session.send_message(mensagem_usuario)
            return response.text
        except Exception as e:
            return f"Erro no chat com o Gemini: {e}"

    def processar_feedback(
        self, relatorio_detalhado: str, ultima_analise: str, feedback_user: str
    ):
        """
        Extrai novos padrões e regras em formato JSON estruturado.
        """
        prompt = f"""Analisa o seguinte feedback do atleta sobre a análise de treino e determina se há algum novo padrão sobre o atleta ou uma nova regra de análise a registar.

RELATÓRIO DE TREINO:
{relatorio_detalhado}

ANÁLISE ANTERIOR:
{ultima_analise}

FEEDBACK DO ATLETA:
{feedback_user}

Responde EXATAMENTE num formato JSON válido com as seguintes chaves:
{{
    "novo_padrao": "descrição do padrão ou null",
    "nova_regra": "descrição da regra ou null"
}}
"""
        try:
            self.ultimo_erro = None
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config
            )

            dados = json.loads(response.text)
            novo_p = dados.get("novo_padrao")
            nova_i = dados.get("nova_regra")
            if novo_p in (None, "null", ""):
                novo_p = None
            if nova_i in (None, "null", ""):
                nova_i = None

            if self.memory_manager:
                if novo_p:
                    self.memory_manager.adicionar_padrao(novo_p)
                if nova_i:
                    self.memory_manager.adicionar_regra(nova_i)
                self.memory_manager.adicionar_feedback(
                    feedback_user,
                    novo_padrao=novo_p,
                    nova_regra=nova_i,
                )

            return True, novo_p, nova_i
        except Exception as e:
            self.ultimo_erro = str(e)
            print(f"Erro ao processar feedback: {e}")
            return False, None, None