import unittest

from core.data_validation import DataValidationError, validate_memory, validate_session


class DataValidationTests(unittest.TestCase):
    def test_valid_documents_are_preserved(self):
        session = {"atividade_id": "a1", "data": "2026-09-06"}
        self.assertEqual(validate_session(session), session)
        self.assertEqual(validate_memory({"padroes_atleta": []})["padroes_atleta"], [])

    def test_invalid_documents_are_rejected(self):
        with self.assertRaises(DataValidationError):
            validate_session({"nome": "sem id"})
        with self.assertRaises(DataValidationError):
            validate_memory({"regras_estilo": {}})


if __name__ == "__main__":
    unittest.main()
