import json
from pathlib import Path

import requests
from config.settings import ATHLETE_ID, FICHEIRO_PERFIL, INTERVALS_API_KEY
from core.data_validation import validate_profile
from core.safe_logging import get_logger


class IntervalsClient:
    def __init__(self, api_key=INTERVALS_API_KEY, athlete_id=ATHLETE_ID):
        self.logger = get_logger("intervals")
        self.api_key = api_key
        self.athlete_id = athlete_id
        self.base_url = "https://intervals.icu/api/v1"
        self.auth = ("API_KEY", self.api_key)

    def _carregar_perfil_guardado(self):
        """Lê o último perfil válido guardado localmente."""
        try:
            if not FICHEIRO_PERFIL.exists() or FICHEIRO_PERFIL.stat().st_size == 0:
                return None
            with open(FICHEIRO_PERFIL, "r", encoding="utf-8") as ficheiro:
                perfil = json.load(ficheiro)
            return perfil if isinstance(perfil, dict) and perfil else None
        except (OSError, json.JSONDecodeError) as e:
            self.logger.warning("Erro ao ler perfil guardado: %s", e)
            return None

    def _guardar_perfil(self, perfil):
        """Guarda localmente um perfil válido obtido da API."""
        try:
            validate_profile(perfil)
            Path(FICHEIRO_PERFIL).parent.mkdir(parents=True, exist_ok=True)
            perfil_existente = self._carregar_perfil_guardado() or {}
            perfil_a_guardar = {**perfil_existente, **perfil}
            with open(FICHEIRO_PERFIL, "w", encoding="utf-8") as ficheiro:
                json.dump(perfil_a_guardar, ficheiro, indent=4, ensure_ascii=False)
            return perfil_a_guardar
        except OSError as e:
            self.logger.error("Erro ao guardar perfil: %s", e)
            return perfil

    def guardar_dados_pessoais(self, dados: dict):
        """Atualiza os dados pessoais sem substituir métricas sincronizadas."""
        perfil = self._carregar_perfil_guardado() or {}
        perfil.update(dados)
        return self._guardar_perfil(perfil)

    def obter_perfil_e_zonas(self):
        """Obtém métricas e configuração de FC, preservando origem e método."""
        try:
            url = f"{self.base_url}/athlete/{self.athlete_id}"
            response = requests.get(url, auth=self.auth, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if not isinstance(data, dict):
                    return None

                sport_settings = data.get("sportSettings", [])
                run_settings = next(
                    (
                        s
                        for s in sport_settings
                        if isinstance(s, dict)
                        and s.get("types", [])
                        and "Run" in s.get("types")
                    ),
                    None,
                )

                max_hr = data.get("icu_max_hr")
                lthr = data.get("icu_lthr")
                resting_hr = data.get("icu_resting_hr")
                zonas = []
                zona_nomes = []
                zona_metodo = None
                zona_origem = "athlete"

                if run_settings:
                    max_hr = run_settings.get("max_hr", max_hr)
                    lthr = run_settings.get("lthr", lthr)
                    resting_hr = run_settings.get("resting_hr", resting_hr)
                    zonas = run_settings.get("hr_zones") or []
                    zona_nomes = run_settings.get("hr_zone_names") or []
                    zona_metodo = run_settings.get("hr_load_type")
                    zona_origem = "sportSettings:Run"

                if not zonas:
                    zonas = data.get("icu_hr_zones") or []
                    if zonas:
                        zona_origem = "athlete:icu_hr_zones"

                perfil = {
                    "max_hr": max_hr,
                    "lthr": lthr,
                    "resting_hr": resting_hr,
                    "zonas_hr": zonas,
                    "zonas_hr_nomes": zona_nomes,
                    "zonas_hr_metodo": zona_metodo or "desconhecido",
                    "zonas_hr_origem": zona_origem,
                }
                return self._guardar_perfil(perfil)
            return self._carregar_perfil_guardado()
        except Exception as e:
            print(f"[EXCEÇÃO] Erro ao obter perfil: {e}")
            return self._carregar_perfil_guardado()

    def obter_corridas(self, data_inicio: str, data_fim: str):
        """Procura corridas no intervalo de datas."""
        try:
            url = f"{self.base_url}/athlete/{self.athlete_id}/activities"
            params = {"oldest": data_inicio, "newest": data_fim}
            response = requests.get(
                url, auth=self.auth, params=params, timeout=10
            )

            if response.status_code == 200:
                atividades = response.json()
                if not isinstance(atividades, list):
                    return []

                corridas = [
                    a
                    for a in atividades
                    if isinstance(a, dict)
                    and (
                        a.get("type") in ["Run", "VirtualRun"]
                        or a.get("icu_type") == "Run"
                    )
                ]
                return corridas
            return []
        except Exception as e:
            print(f"[EXCEÇÃO] Erro ao procurar corridas: {e}")
            return []

    def obter_laps_atividade(self, activity_id: str):
        """
        Obtém os intervalos/laps diretamente do endpoint /activity/{id}/intervals.
        """
        try:
            url = f"{self.base_url}/activity/{activity_id}/intervals"
            response = requests.get(url, auth=self.auth, timeout=10)

            if response.status_code == 200:
                data = response.json()
                
                # Se a API responder diretamente com uma lista de intervalos
                if isinstance(data, list) and len(data) > 0:
                    laps = []
                    for idx, item in enumerate(data, start=1):
                        dist_m = item.get("distance", 0)
                        moving_sec = item.get("moving_time", item.get("elapsed_time", 0))
                        laps.append({
                            "distance": dist_m,
                            "elapsed_time": moving_sec,
                            "moving_time": moving_sec,
                            "average_heartrate": item.get("average_heartrate", item.get("average_hr", 0)),
                            "max_heartrate": item.get("max_heartrate", item.get("max_hr", 0)),
                            "label": item.get("label", item.get("type", item.get("name", f"Lap {idx}")))
                        })
                    return laps
                
                # Se responder com um objeto contendo a lista de intervalos
                elif isinstance(data, dict):
                    icu_intervals = data.get("icu_intervals") or data.get("intervals") or []
                    if isinstance(icu_intervals, list) and len(icu_intervals) > 0:
                        laps = []
                        for idx, item in enumerate(icu_intervals, start=1):
                            dist_m = item.get("distance", 0)
                            moving_sec = item.get("moving_time", item.get("elapsed_time", 0))
                            laps.append({
                                "distance": dist_m,
                                "elapsed_time": moving_sec,
                                "moving_time": moving_sec,
                                "average_heartrate": item.get("average_heartrate", item.get("average_hr", 0)),
                                "max_heartrate": item.get("max_heartrate", item.get("max_hr", 0)),
                                "label": item.get("label", item.get("type", f"Intervalo {idx}"))
                            })
                        return laps
        except Exception as e:
            print(f"[EXCEÇÃO] Erro ao obter laps da atividade {activity_id}: {e}")

        return []