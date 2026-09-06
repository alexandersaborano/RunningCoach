"""Providers e orquestração de agentes especializados de treino."""

from dataclasses import dataclass
import os
from typing import Protocol

import requests
from google.genai import types


class AgentProvider(Protocol):
    def generate(self, prompt: str) -> str:
        """Gera uma resposta para o prompt do agente."""


class GeminiProvider:
    def __init__(self, client, model_id: str):
        self.client = client
        self.model_id = model_id

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            ),
        )
        return response.text


class OpenAIProvider:
    def __init__(self, api_key: str, model_id: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_id = model_id

    def generate(self, prompt: str) -> str:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model_id,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class AnthropicProvider:
    def __init__(self, api_key: str, model_id: str = "claude-3-5-haiku-latest"):
        self.api_key = api_key
        self.model_id = model_id

    def generate(self, prompt: str) -> str:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model_id,
                "max_tokens": 2048,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    responsibility: str
    provider: str = "gemini"


AGENT_DEFINITIONS = (
    AgentDefinition(
        "carga",
        "Avaliar volume, TSS e risco de excesso.",
        os.getenv("AGENT_CARGA_PROVIDER", "gemini"),
    ),
    AgentDefinition(
        "fisiologia",
        "Avaliar relação entre pace, FC e eficiência.",
        os.getenv("AGENT_FISIOLOGIA_PROVIDER", "gemini"),
    ),
    AgentDefinition(
        "treino",
        "Comparar prescrição, execução e consistência.",
        os.getenv("AGENT_TREINO_PROVIDER", "gemini"),
    ),
    AgentDefinition(
        "critico",
        "Detetar erros, lacunas e riscos nas conclusões.",
        os.getenv("AGENT_CRITICO_PROVIDER", "gemini"),
    ),
)


class AgentRegistry:
    def __init__(self):
        self._providers = {}

    def register(self, name: str, provider: AgentProvider):
        self._providers[name] = provider

    def get(self, name: str) -> AgentProvider:
        if name not in self._providers:
            raise KeyError(f"Provider de IA não configurado: {name}")
        return self._providers[name]


class SpecializedAgentRunner:
    """Executa agentes especializados e consolida as respostas num coordenador."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def run(self, context: str) -> str:
        reports = []
        for definition in AGENT_DEFINITIONS:
            prompt = f"""És o agente especializado de {definition.name} de um treinador de corrida.
Responsabilidade: {definition.responsibility}
Analisa apenas os dados fornecidos, sê específico e identifica limitações.
Responde em Português com conclusões acionáveis.

CONTEXTO:
{context}
"""
            try:
                result = self.registry.get(definition.provider).generate(prompt)
                reports.append(f"[{definition.name.upper()}]\n{result}")
            except Exception as error:
                reports.append(
                    f"[{definition.name.upper()}]\nAgente indisponível: {error}"
                )

        coordinator = self.registry.get("gemini")
        reports_text = "\n\n".join(reports)
        synthesis_prompt = f"""És o coordenador de um sistema multiagente de treino.
Consolida os relatórios abaixo num plano progressivo em Português.
Distingue evidência, hipótese e recomendação. Não inventes dados.

RELATÓRIOS DOS AGENTES:
{reports_text}
"""
        return coordinator.generate(synthesis_prompt)
