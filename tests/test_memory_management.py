import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.memory_manager import MemoryManager


class MemoryManagementTests(unittest.TestCase):
    def test_can_list_toggle_and_remove_memory_without_losing_feedback(self):
        with tempfile.TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memory.json"
            with patch("core.memory_manager.FICHEIRO_MEMORIA", memory_path):
                manager = MemoryManager(memory_path)
                manager.adicionar_padrao("Treinar com progressão")
                manager.adicionar_feedback("Senti fadiga.")

                items = manager.listar_memorias_geriveis()
                self.assertEqual(len(items), 1)
                manager.atualizar_memoria_gerivel(items[0]["id"], ativo=False)
                self.assertEqual(manager.carregar_memoria()["padroes_atleta"], [])
                self.assertEqual(len(manager.carregar_memoria()["historico_feedback"]), 1)

                manager.atualizar_memoria_gerivel(items[0]["id"], ativo=True)
                self.assertEqual(manager.carregar_memoria()["padroes_atleta"], ["Treinar com progressão"])
                manager.atualizar_memoria_gerivel(items[0]["id"], remover=True)
                self.assertEqual(manager.listar_memorias_geriveis(), [])


if __name__ == "__main__":
    unittest.main()
