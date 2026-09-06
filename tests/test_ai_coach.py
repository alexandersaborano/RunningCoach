import unittest
from unittest.mock import Mock, patch

from core.ai_coach import AICoach


class AICoachTests(unittest.TestCase):
    def test_missing_gemini_key_does_not_crash_startup(self):
        with patch("core.ai_coach.GEMINI_API_KEY", ""):
            coach = AICoach()

        self.assertFalse(coach.disponivel)
        self.assertIn("GEMINI_API_KEY", coach.config_error)

    def test_global_analysis_includes_recovery_context(self):
        response = Mock(text="análise global")
        client = Mock()
        client.models.generate_content.return_value = response
        coach = AICoach.__new__(AICoach)
        coach.client = client
        coach.model_id = "test-model"

        result = coach.analisar_historico_global(
            [{
                "data": "2026-09-05T08:00:00",
                "nome": "Corrida",
                "distancia_km": 10,
                "pace_min_km": 5.5,
                "fc_media": 150,
                "carga_tss": 60,
            }],
            {
                "2026-09-05": {
                    "sono_horas": 7.5,
                    "recuperacao": 8,
                    "fc_repouso": 52,
                }
            },
        )

        prompt = client.models.generate_content.call_args.kwargs["contents"]
        self.assertEqual(result, "análise global")
        self.assertIn("sono 7.5 h", prompt)
        self.assertIn("recuperação 8/10", prompt)
        self.assertIn("FC repouso 52 bpm", prompt)

    def test_global_analysis_handles_empty_history(self):
        coach = AICoach.__new__(AICoach)

        self.assertEqual(
            coach.analisar_historico_global([]),
            "Não existem sessões suficientes para uma análise global.",
        )

    def test_specialized_agents_are_orchestrated(self):
        class Provider:
            def __init__(self, name):
                self.name = name
                self.prompts = []

            def generate(self, prompt):
                self.prompts.append(prompt)
                return self.name

        from core.ai_agents import AgentRegistry, SpecializedAgentRunner

        registry = AgentRegistry()
        coordinator = Provider("coordinator")
        registry.register("gemini", coordinator)
        for name in ["carga", "fisiologia", "treino", "critico"]:
            registry.register("gemini", coordinator)

        result = SpecializedAgentRunner(registry).run("dados de teste")

        self.assertEqual(result, "coordinator")
        self.assertEqual(len(coordinator.prompts), 5)

    def test_global_analysis_includes_individual_analysis(self):
        response = Mock(text="análise")
        client = Mock()
        client.models.generate_content.return_value = response
        coach = AICoach.__new__(AICoach)
        coach.client = client
        coach.model_id = "test-model"

        coach.analisar_historico_global([{
            "data": "2026-09-05",
            "nome": "Intervalado",
            "analise": "A execução mostrou evolução no pace.",
        }])

        prompt = client.models.generate_content.call_args.kwargs["contents"]
        self.assertIn("ANÁLISES INDIVIDUAIS RELEVANTES", prompt)
        self.assertIn("A execução mostrou evolução no pace.", prompt)


if __name__ == "__main__":
    unittest.main()
