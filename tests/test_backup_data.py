import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import backup_data


class BackupDataTests(unittest.TestCase):
    def test_backup_retention_and_integrity(self):
        with tempfile.TemporaryDirectory() as temporary:
            raiz = Path(temporary)
            dados = raiz / "data"
            backups = raiz / "backups"
            dados.mkdir()
            (dados / "perfil.json").write_text('{"idade": 34}', encoding="utf-8")

            with patch.object(backup_data, "DATA_DIR", dados), patch.object(
                backup_data, "BACKUP_DIR", backups
            ):
                primeiro = backup_data.criar_backup(retencao=1)
                segundo = backup_data.criar_backup(retencao=1)

                self.assertFalse(primeiro.exists())
                self.assertTrue(segundo.exists())
                self.assertEqual(backup_data.verificar_integridade(segundo), [])

    def test_invalid_json_is_reported_and_not_restored(self):
        with tempfile.TemporaryDirectory() as temporary:
            origem = Path(temporary) / "backup"
            destino = Path(temporary) / "data"
            origem.mkdir()
            (origem / "memoria.json").write_text("{invalid", encoding="utf-8")
            destino.mkdir()
            (destino / "original.json").write_text("{}", encoding="utf-8")

            with self.assertRaises(ValueError):
                backup_data.restaurar_backup(origem, destino)

            self.assertTrue((destino / "original.json").exists())


if __name__ == "__main__":
    unittest.main()
