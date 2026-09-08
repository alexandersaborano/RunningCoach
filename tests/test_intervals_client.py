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

    def test_maps_run_sport_settings_without_assuming_hrr(self):
        response = Mock(status_code=200)
        response.json.return_value = {
            "icu_max_hr": 190,
            "icu_lthr": 165,
            "icu_resting_hr": 52,
            "sportSettings": [{
                "types": ["Run"],
                "max_hr": 188,
                "lthr": 162,
                "resting_hr": 51,
                "hr_zones": [120, 145, 162, 175, 188],
                "hr_zone_names": ["Z1", "Z2", "Z3", "Z4", "Z5"],
                "hr_load_type": "LTHR",
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            profile_path = Path(directory) / "profile.json"
            with patch("core.intervals_client.FICHEIRO_PERFIL", profile_path):
                with patch("core.intervals_client.requests.get", return_value=response):
                    profile = IntervalsClient().obter_perfil_e_zonas()

        self.assertEqual(profile["max_hr"], 188)
        self.assertEqual(profile["lthr"], 162)
        self.assertEqual(profile["resting_hr"], 51)
        self.assertEqual(profile["zonas_hr_origem"], "sportSettings:Run")
        self.assertEqual(profile["zonas_hr_metodo"], "LTHR")
        self.assertEqual(profile["zonas_hr_nomes"], ["Z1", "Z2", "Z3", "Z4", "Z5"])

    def test_saves_parallel_zone_profiles_and_switches_active_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            profile_path = Path(directory) / "profile.json"
            with patch("core.intervals_client.FICHEIRO_PERFIL", profile_path):
                client = IntervalsClient()
                client._guardar_perfil({
                    "max_hr": 190,
                    "resting_hr": 50,
                    "perfis_zonas": {
                        "intervals_icu": {
                            "limites": [120, 150],
                            "nomes": ["Z1", "Z2"],
                            "metodo": "LTHR",
                            "origem": "sportSettings:Run",
                        },
                        "hrr_karvonen": {
                            "limites": [120, 162],
                            "nomes": ["Z1", "Z2"],
                            "metodo": "%HRR (Karvonen)",
                            "origem": "calculado_localmente",
                        },
                    },
                    "perfil_zonas_ativo": "intervals_icu",
                })

                profile = client.guardar_perfil_zonas_ativo("hrr_karvonen")

        self.assertEqual(profile["perfil_zonas_ativo"], "hrr_karvonen")
        self.assertEqual(profile["zonas_hr"], [120, 162])
        self.assertEqual(profile["zonas_hr_origem"], "calculado_localmente")
        self.assertIn("intervals_icu", profile["perfis_zonas"])

    def test_fetches_and_normalizes_wellness(self):
        response = Mock(status_code=200)
        response.json.return_value = [{
            "id": "w1", "date": "2026-09-08", "sleepSecs": 27000,
            "readiness": 8, "restingHR": 49, "hrv": 62,
        }]
        with patch("core.intervals_client.requests.get", return_value=response) as request:
            records = IntervalsClient().obter_bem_estar("2026-09-01", "2026-09-08")
        self.assertEqual(records[0]["sono_horas"], 7.5)
        self.assertEqual(records[0]["fc_repouso"], 49)
        self.assertEqual(records[0]["origem"], "intervals_icu")
        request.assert_called_once()


if __name__ == "__main__":
    unittest.main()
