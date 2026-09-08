import json
from pathlib import Path

import requests
from config.settings import ATHLETE_ID, FICHEIRO_PERFIL, INTERVALS_API_KEY
from core.data_validation import validate_profile
from core.data_validation import validate_wellness_records
from core.heart_rate_zones import calcular_zonas_hrr
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

    def guardar_perfil_zonas_ativo(self, nome: str):
        """Seleciona um perfil de zonas sem apagar as restantes configurações."""
        perfil = self._carregar_perfil_guardado() or {}
        perfis = perfil.get("perfis_zonas", {})
        selecionado = perfis.get(nome)
        if not isinstance(selecionado, dict):
            raise ValueError(f"Perfil de zonas desconhecido: {nome}")
        perfil["perfil_zonas_ativo"] = nome
        perfil.update({
            "zonas_hr": selecionado.get("limites", []),
            "zonas_hr_nomes": selecionado.get("nomes", []),
            "zonas_hr_metodo": selecionado.get("metodo", "desconhecido"),
            "zonas_hr_origem": selecionado.get("origem", nome),
        })
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

                perfis_zonas = {
                    "intervals_icu": {
                        "limites": zonas,
                        "nomes": zona_nomes,
                        "metodo": zona_metodo or "desconhecido",
                        "origem": zona_origem,
                    }
                }
                try:
                    zonas_hrr = calcular_zonas_hrr(max_hr, resting_hr)
                except ValueError:
                    zonas_hrr = []
                if zonas_hrr:
                    perfis_zonas["hrr_karvonen"] = {
                        "limites": zonas_hrr,
                        "nomes": [f"Z{i}" for i in range(1, len(zonas_hrr) + 1)],
                        "percentagens": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                        "metodo": "%HRR (Karvonen)",
                        "origem": "calculado_localmente",
                    }
                perfil_existente = self._carregar_perfil_guardado() or {}
                perfil_ativo = perfil_existente.get("perfil_zonas_ativo", "intervals_icu")
                if perfil_ativo == "hrr_karvonen" and "hrr_karvonen" in perfis_zonas:
                    fonte_ativa = perfis_zonas["hrr_karvonen"]
                else:
                    perfil_ativo = "intervals_icu"
                    fonte_ativa = perfis_zonas["intervals_icu"]
                perfil = {
                    "max_hr": max_hr,
                    "lthr": lthr,
                    "resting_hr": resting_hr,
                    "zonas_hr": fonte_ativa["limites"],
                    "zonas_hr_nomes": fonte_ativa["nomes"],
                    "zonas_hr_metodo": fonte_ativa["metodo"],
                    "zonas_hr_origem": fonte_ativa["origem"],
                    "perfis_zonas": perfis_zonas,
                    "perfil_zonas_ativo": perfil_ativo,
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

    def obter_bem_estar(self, data_inicio: str, data_fim: str):
        """Obtém e normaliza os registos de wellness do Intervals.icu."""
        if not data_inicio or not data_fim:
            raise ValueError("É necessário indicar o intervalo de wellness.")
        url = f"{self.base_url}/athlete/{self.athlete_id}/wellness"
        try:
            response = requests.get(
                url, auth=self.auth,
                params={"oldest": data_inicio, "newest": data_fim}, timeout=10
            )
            if response.status_code != 200:
                self.logger.warning("Wellness devolveu HTTP %s", response.status_code)
                return []
            payload = response.json()
        except (requests.RequestException, ValueError) as error:
            self.logger.warning("Não foi possível obter wellness: %s", error)
            return []
        if not isinstance(payload, list):
            self.logger.warning("Resposta de wellness inválida: esperada uma lista")
            return []
        records = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            data = item.get("date") or item.get("data")
            if not isinstance(data, str) or not data.strip():
                continue
            record = {"data": data[:10], "origem": "intervals_icu"}
            for source, target in (
                ("sleepSecs", "sono_horas"), ("sleep_hours", "sono_horas"),
                ("sleepScore", "qualidade_sono"), ("readiness", "recuperacao"),
                ("recovery", "recuperacao"), ("restingHR", "fc_repouso"),
                ("resting_hr", "fc_repouso"), ("hrv", "hrv"),
                ("fatigue", "fadiga"), ("soreness", "dor_muscular"),
                ("stress", "stress"), ("mood", "humor"), ("weight", "peso_kg"),
            ):
                if source in item and item[source] is not None:
                    value = item[source]
                    if source == "sleepSecs":
                        try:
                            value = float(value) / 3600
                        except (TypeError, ValueError):
                            continue
                    record[target] = value
            record["intervals_id"] = item.get("id", record["data"])
            records.append(record)
        try:
            return validate_wellness_records(records)
        except ValueError as error:
            self.logger.warning("Registos de wellness inválidos: %s", error)
            return []

    obter_wellness = obter_bem_estar

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