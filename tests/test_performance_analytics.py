import unittest

from core.performance_analytics import (
    aggregate_weekly,
    classify_intensity,
    compare_equivalent_periods,
    consolidated_export_data,
    export_csv,
    export_json,
    filter_sessions,
)


class PerformanceAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.sessions = [
            {"atividade_id": "1", "data": "2026-09-01", "distancia_km": 10, "tempo_movimento_min": 60, "carga_tss": 80, "fc_media": 135, "type": "Run"},
            {"atividade_id": "2", "data": "2026-09-03", "distancia_km": 5, "tempo_movimento_min": 25, "carga_tss": 50, "fc_media": 165, "type": "Run"},
            {"atividade_id": "3", "data": "2026-08-25", "distancia_km": 8, "tempo_movimento_min": 48, "carga_tss": 60, "fc_media": 130, "type": "Ride"},
        ]

    def test_weekly_metrics_and_intensity(self):
        rows = aggregate_weekly(self.sessions)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]["distance_km"], 15)
        self.assertEqual(classify_intensity(self.sessions[1]), "hard")

    def test_comparison_filter_and_exports(self):
        filtered = filter_sessions(self.sessions, workout_type="Run", start="2026-09-01", intensity="easy")
        self.assertEqual([x["atividade_id"] for x in filtered], ["1"])
        comparison = compare_equivalent_periods(self.sessions[:2], self.sessions[2:])
        self.assertEqual(comparison["delta"]["distance_km"], 7)
        records = consolidated_export_data(self.sessions, feedback=[{"note": "ok"}])
        self.assertIn('"record_type": "completed"', export_json(records))
        self.assertIn("record_type", export_csv(records))


if __name__ == "__main__":
    unittest.main()
