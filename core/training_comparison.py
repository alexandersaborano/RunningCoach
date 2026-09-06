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
