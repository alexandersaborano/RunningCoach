import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from core.ai_evolution import (
    avaliar_resultado_recomendacao,
    calcular_sinais_fadiga,
    resumir_semana,
    selecionar_provider,
)
from core.memory_manager import MemoryManager


class AIEvolutionTests(unittest.TestCase):
    def test_weekly_summary_and_fatigue_signals_are_deterministic(self):
        sessions = [
            {"atividade_id": "a1", "data": "2026-09-01", "distancia_km": 10, "carga_tss": 180},
            {"atividade_id": "a2", "data": "2026-09-03", "distancia_km": 8, "carga_tss": 180},
        ]
        recovery = {"2026-09-01": {"recuperacao": 4, "sono_horas": 6}}
        first = resumir_semana(sessions, recovery, "2026-08-31")
        self.assertEqual(first["distancia_km"], 18)
        self.assertEqual(first["sinais_fadiga"]["nivel"], "alto")
        self.assertEqual(first, resumir_semana(sessions, recovery, "2026-08-31"))

    def test_recommendation_outcome_uses_adherence_and_feedback(self):
        result = avaliar_resultado_recomendacao(
            "reduzir intensidade",
            [{"executada": True}, {"executada": False}],
            feedback="Foi útil",
        )
        self.assertEqual(result["resultado"], "favoravel")
        self.assertEqual(result["adesao"], 0.5)

    def test_provider_selection_falls_back_without_private_registry_access(self):
        registry = Mock()
        registry.get.side_effect = [KeyError("openai"), "gemini-provider"]
        provider, name = selecionar_provider(registry, "openai", ("gemini",))
        self.assertEqual((provider, name), ("gemini-provider", "gemini"))

    def test_memory_persists_ai_records_and_migrates_legacy_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.json"
            path.write_text(json.dumps({"padroes_observados": ["facto"], "instrucoes_de_estilo": ["regra"]}), encoding="utf-8")
            manager = MemoryManager(path)
            memory = manager.carregar_memoria()
            self.assertEqual(memory["padroes_atleta"], ["facto"])
            self.assertEqual(memory["padroes_atleta_entradas"][0]["origem"], "legado")
            self.assertIn("criado_em", memory["regras_estilo_entradas"][0])
            manager.guardar_resumo_semanal({"semana_inicio": "2026-08-31", "sessoes": 2})
            manager.guardar_resultado_recomendacao({"resultado": "favoravel"})
            reloaded = MemoryManager(path).carregar_memoria()
            self.assertEqual(len(reloaded["resumos_semanais_ai"]), 1)
            self.assertEqual(reloaded["resultados_recomendacoes"][0]["resultado"], "favoravel")


if __name__ == "__main__":
    unittest.main()
