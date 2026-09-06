import tempfile
import unittest
from pathlib import Path

from core.planned_workouts import PlannedWorkoutError, PlannedWorkoutStore, merge_planned_completed


class PlannedWorkoutTests(unittest.TestCase):
    def test_crud_persists_and_validates(self):
        with tempfile.TemporaryDirectory() as folder:
            store = PlannedWorkoutStore(Path(folder) / "planned.json")
            workout = store.create({"date": "2026-09-10", "name": "Easy run", "distance_km": 6})
            self.assertEqual(store.get(workout["id"])["name"], "Easy run")
            changed = store.update(workout["id"], {"duration_min": 40})
            self.assertEqual(changed["duration_min"], 40.0)
            self.assertTrue(store.delete(workout["id"]))
            self.assertEqual(store.list(), [])
            with self.assertRaises(PlannedWorkoutError):
                store.create({"date": "not-a-date", "name": "Bad"})

    def test_merge_marks_sources_and_sorts(self):
        rows = merge_planned_completed(
            [{"date": "2026-09-10", "name": "planned"}],
            [{"data": "2026-09-02", "nome": "completed"}],
        )
        self.assertEqual([row["source"] for row in rows], ["completed", "planned"])


if __name__ == "__main__":
    unittest.main()
