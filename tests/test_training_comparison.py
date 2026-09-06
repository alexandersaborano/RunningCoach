import unittest

from core.training_comparison import construir_comparacao


class TrainingComparisonTests(unittest.TestCase):
    def test_builds_prescription_and_actual_metrics(self):
        comparison = construir_comparacao(
            {
                "distance": 10500,
                "moving_time": 3600,
                "average_heartrate": 150,
                "max_heartrate": 175,
                "icu_training_load": 90,
            },
            "10 km com 4 intervalos",
        )

        self.assertEqual(comparison["prescricao"], "10 km com 4 intervalos")
        self.assertEqual(comparison["realizado"]["distancia_km"], 10.5)
        self.assertEqual(comparison["realizado"]["tempo_movimento_min"], 60.0)
        self.assertEqual(comparison["realizado"]["carga_tss"], 90)


if __name__ == "__main__":
    unittest.main()
