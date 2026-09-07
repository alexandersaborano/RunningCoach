import unittest

import pandas as pd

from ui.table_actions import preparar_tabela


class TableActionsTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            [
                {"nome": "Long run", "distancia": 20, "nota": None},
                {"nome": "Easy run", "distancia": 5, "nota": "leve"},
                {"nome": "Intervals", "distancia": 10, "nota": "forte"},
            ]
        )

    def test_filters_text_without_regex_interpretation(self):
        result = preparar_tabela(self.data, query="run|intervals")
        self.assertEqual(len(result), 0)

        result = preparar_tabela(self.data, query="run")
        self.assertEqual(result["nome"].tolist(), ["Long run", "Easy run"])

    def test_sorts_numbers_and_preserves_selected_columns(self):
        result = preparar_tabela(
            self.data,
            sort_column="distancia",
            descending=True,
            columns=["nome", "distancia"],
        )
        self.assertEqual(result["distancia"].tolist(), [20, 10, 5])
        self.assertEqual(result.columns.tolist(), ["nome", "distancia"])


if __name__ == "__main__":
    unittest.main()
