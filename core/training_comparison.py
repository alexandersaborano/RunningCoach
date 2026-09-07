from collections.abc import Mapping, Sequence


def extrair_prescricao_intervals(corrida: Mapping) -> str:
    """Extrai texto de prescrição dos formatos conhecidos do Intervals.icu."""
    candidatos = [
        corrida.get("description"),
        corrida.get("workout_description"),
        corrida.get("workout_text"),
    ]
    workout_doc = corrida.get("workout_doc")
    if isinstance(workout_doc, Mapping):
        candidatos.extend([
            workout_doc.get("description"),
            workout_doc.get("text"),
            workout_doc.get("workout"),
        ])
    for candidato in candidatos:
        if isinstance(candidato, str) and candidato.strip():
            return candidato.strip()
    return ""


def encontrar_prescricao_local(
    treinos: Sequence[Mapping],
    data_treino: str,
) -> str:
    """Obtém a prescrição local do treino planeado correspondente à data."""
    data_iso = str(data_treino or "")[:10]
    for treino in treinos:
        if str(treino.get("date") or treino.get("data") or "")[:10] != data_iso:
            continue
        partes = [
            treino.get("name") or treino.get("nome") or treino.get("title"),
            treino.get("prescription") or treino.get("prescricao"),
        ]
        texto = "\n".join(str(parte).strip() for parte in partes if parte and str(parte).strip())
        if texto:
            return texto
    return ""


def construir_comparacao(corrida: dict, descricao_plano: str) -> dict:
    """Organiza a prescrição e as métricas realizadas para comparação."""
    return {
        "prescricao": descricao_plano or "Sem prescrição disponível.",
        "realizado": {
            "distancia_km": round((corrida.get("distance") or 0) / 1000, 2),
            "tempo_movimento_min": round((corrida.get("moving_time") or 0) / 60, 2),
            "fc_media": corrida.get("average_heartrate"),
            "fc_maxima": corrida.get("max_heartrate"),
            "carga_tss": corrida.get("icu_training_load"),
        },
    }
