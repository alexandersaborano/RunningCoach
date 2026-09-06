import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.memory_manager import MemoryManager


class MemoryManagerTests(unittest.TestCase):
    def test_saves_and_loads_recovery_by_date(self):
        with tempfile.TemporaryDirectory() as directory:
            recovery_path = Path(directory) / "recovery.json"
            memory_path = Path(directory) / "memory.json"
            with patch("core.memory_manager.FICHEIRO_RECUPERACAO", recovery_path):
                manager = MemoryManager(memory_path)
                manager.guardar_recuperacao("2026-09-05", 7.5, 8, 52)

                self.assertEqual(
                    manager.carregar_recuperacao("2026-09-05"),
                    {
                        "data": "2026-09-05",
                        "sono_horas": 7.5,
                        "recuperacao": 8,
                        "fc_repouso": 52,
                    },
                )

    def test_imports_sessions_without_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history"
            memory_path = Path(directory) / "memory.json"
            with patch("core.memory_manager.HISTORICO_DIR", history_path):
                manager = MemoryManager(memory_path)
                imported = [
                    {"atividade_id": "a1", "data": "2026-09-01"},
                    {"atividade_id": "a2", "data": "2026-09-02"},
                    {"atividade_id": "a1", "data": "2026-09-03"},
                ]

                self.assertEqual(manager.guardar_sessoes_importadas(imported), 2)
                self.assertEqual(len(manager.carregar_historico_sessoes()), 2)

                self.assertEqual(manager.guardar_sessoes_importadas(imported), 0)

    def test_migrates_legacy_memory_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memory.json"
            memory_path.write_text(
                json.dumps({
                    "padroes_observados": ["facto"],
                    "instrucoes_de_estilo": ["regra"],
                }),
                encoding="utf-8",
            )
            manager = MemoryManager(memory_path)

            memory = manager.carregar_memoria()

            self.assertEqual(memory["padroes_atleta"], ["facto"])
            self.assertEqual(memory["regras_estilo"], ["regra"])
            self.assertEqual(memory["historico_feedback"], [])

    def test_saves_and_loads_global_analysis_context(self):
        with tempfile.TemporaryDirectory() as directory:
            analysis_directory = Path(directory) / "global"
            memory_path = Path(directory) / "memory.json"
            with patch("core.memory_manager.ANALISES_GLOBAIS_DIR", analysis_directory):
                manager = MemoryManager(memory_path)
                manager.guardar_analise_global({
                    "data": "2026-09-05T12:00:00",
                    "atividade_ids": ["a1"],
                    "analise": "progressão consistente",
                })

                analyses = manager.carregar_analises_globais()

                self.assertEqual(len(analyses), 1)
                self.assertEqual(analyses[0]["atividade_ids"], ["a1"])


if __name__ == "__main__":
    unittest.main()
