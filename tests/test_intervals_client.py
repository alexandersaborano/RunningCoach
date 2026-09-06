import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from core.intervals_client import IntervalsClient


class IntervalsClientTests(unittest.TestCase):
    def test_saves_profile_and_preserves_personal_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            profile_path = Path(directory) / "profile.json"
            response = Mock(status_code=200)
            response.json.return_value = {
                "icu_max_hr": 190,
                "icu_lthr": 165,
                "icu_resting_hr": 50,
                "icu_hr_zones": [120, 145, 165],
            }
            with patch("core.intervals_client.FICHEIRO_PERFIL", profile_path):
                client = IntervalsClient()
                client.guardar_dados_pessoais({"peso_kg": 72.5, "idade": 35})

                with patch("core.intervals_client.requests.get", return_value=response):
                    profile = client.obter_perfil_e_zonas()

                self.assertEqual(profile["peso_kg"], 72.5)
                self.assertEqual(profile["idade"], 35)
                self.assertEqual(json.loads(profile_path.read_text())["max_hr"], 190)

    def test_uses_cached_profile_when_api_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            profile_path = Path(directory) / "profile.json"
            cached = {"max_hr": 190, "lthr": 165, "resting_hr": 50, "zonas_hr": []}
            profile_path.write_text(json.dumps(cached), encoding="utf-8")
            with patch("core.intervals_client.FICHEIRO_PERFIL", profile_path):
                with patch(
                    "core.intervals_client.requests.get",
                    side_effect=ConnectionError("offline"),
                ):
                    self.assertEqual(IntervalsClient().obter_perfil_e_zonas(), cached)


if __name__ == "__main__":
    unittest.main()
