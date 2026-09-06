"""Evidência determinística para a evolução do treinador AI.

Este módulo não chama providers nem serviços externos.  Os seus resultados são
deliberadamente simples, auditáveis e adequados para serem incluídos num prompt.
"""

from datetime import date, datetime, timedelta
from statistics import mean
from typing import Iterable, Mapping, Optional


def _day(value) -> Optional[date]:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except (TypeError, ValueError):
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None


def _number(item, *names, default=0.0):
    for name in names:
        value = item.get(name) if isinstance(item, Mapping) else None
        try:
            return float(value)
        except (TypeError, ValueError):
            pass
    return default


def _week_start(reference=None):
    reference = _day(reference) or date.today()
    return reference - timedelta(days=reference.weekday())


def calcular_sinais_fadiga(
    sessoes: Iterable[Mapping],
    recuperacao_por_data: Optional[Mapping] = None,
    data_referencia=None,
):
    """Calcula sinais explicáveis de carga e recuperação dos últimos 7 dias."""
    recovery = recuperacao_por_data or {}
    end = _day(data_referencia) or date.today()
    start = end - timedelta(days=6)
    selected = [s for s in sessoes or [] if start <= (_day(s.get("data")) or start - timedelta(days=1)) <= end]
    loads = [_number(s, "carga_tss", "tss") for s in selected]
    recovery_values = []
    sleep_values = []
    resting_values = []
    for session in selected:
        data = (_day(session.get("data")) or start).isoformat()
        item = recovery.get(data, {})
        if item.get("recuperacao") is not None:
            recovery_values.append(_number(item, "recuperacao"))
        if item.get("sono_horas") is not None:
            sleep_values.append(_number(item, "sono_horas"))
        if item.get("fc_repouso") is not None:
            resting_values.append(_number(item, "fc_repouso"))

    sinais = []
    total_load = sum(loads)
    if total_load >= 350:
        sinais.append({"tipo": "carga_alta", "valor": round(total_load, 2), "gravidade": "alta"})
    elif total_load >= 250:
        sinais.append({"tipo": "carga_elevada", "valor": round(total_load, 2), "gravidade": "moderada"})
    if recovery_values and mean(recovery_values) < 5:
        sinais.append({"tipo": "recuperacao_baixa", "valor": round(mean(recovery_values), 2), "gravidade": "alta"})
    if sleep_values and mean(sleep_values) < 6.5:
        sinais.append({"tipo": "sono_insuficiente", "valor": round(mean(sleep_values), 2), "gravidade": "moderada"})
    if len(resting_values) >= 2 and max(resting_values) - min(resting_values) >= 5:
        sinais.append({"tipo": "fc_repouso_instavel", "valor": round(max(resting_values) - min(resting_values), 2), "gravidade": "moderada"})
    nivel = "alto" if any(s["gravidade"] == "alta" for s in sinais) else ("moderado" if sinais else "baixo")
    return {
        "periodo": {"inicio": start.isoformat(), "fim": end.isoformat()},
        "carga_total": round(total_load, 2),
        "sinais": sinais,
        "nivel": nivel,
    }


def resumir_semana(sessoes: Iterable[Mapping], recuperacao_por_data=None, inicio_semana=None):
    """Produz um resumo semanal estável, sem inferências de um modelo."""
    start = _week_start(inicio_semana)
    end = start + timedelta(days=6)
    selected = [s for s in sessoes or [] if start <= (_day(s.get("data")) or start - timedelta(days=1)) <= end]
    distances = [_number(s, "distancia_km", "distancia") for s in selected]
    loads = [_number(s, "carga_tss", "tss") for s in selected]
    paces = [_number(s, "pace_min_km", "pace") for s in selected if _number(s, "pace_min_km", "pace", default=0)]
    rec = (recuperacao_por_data or {})
    recovery = [_number(rec.get((_day(s.get("data")) or start).isoformat(), {}), "recuperacao")
                for s in selected if rec.get((_day(s.get("data")) or start).isoformat(), {}).get("recuperacao") is not None]
    summary = {
        "semana_inicio": start.isoformat(),
        "semana_fim": end.isoformat(),
        "sessoes": len(selected),
        "distancia_km": round(sum(distances), 2),
        "carga_tss": round(sum(loads), 2),
        "pace_medio_min_km": round(mean(paces), 2) if paces else None,
        "recuperacao_media": round(mean(recovery), 2) if recovery else None,
        "atividade_ids": [s.get("atividade_id") for s in selected if s.get("atividade_id")],
    }
    summary["sinais_fadiga"] = calcular_sinais_fadiga(selected, rec, end)
    summary["evidencia"] = {
        "dados_observados": ["sessoes", "distancia_km", "carga_tss"] + (["recuperacao"] if recovery else []),
        "limitacoes": [] if selected else ["sem_sessoes_no_periodo"],
    }
    return summary


def avaliar_resultado_recomendacao(recomendacao, sessoes_posteriores=None, feedback=None):
    """Avalia uma recomendação apenas contra resultados observáveis posteriores."""
    sessions = list(sessoes_posteriores or [])
    completed = [s for s in sessions if s.get("concluida", s.get("executada", True)) is not False]
    adherence = len(completed) / len(sessions) if sessions else None
    result = "sem_evidencia"
    if adherence is not None:
        result = "favoravel" if adherence >= 0.75 else ("parcial" if adherence >= 0.5 else "desfavoravel")
    if feedback:
        text = str(feedback).lower()
        if any(word in text for word in ("útil", "util", "ajudou", "boa")):
            result = "favoravel"
        elif any(word in text for word in ("inútil", "inutil", "não ajud", "nao ajud", "ruim")):
            result = "desfavoravel"
    return {
        "recomendacao": recomendacao,
        "resultado": result,
        "sessoes_avaliadas": len(sessions),
        "adesao": round(adherence, 3) if adherence is not None else None,
        "feedback": feedback,
        "avaliado_em": datetime.now().isoformat(timespec="seconds"),
    }


def selecionar_provider(registry, provider=None, fallback=("gemini",)):
    """Obtém um provider configurado sem aceder a atributos privados do registry."""
    nomes = [provider] if provider else []
    if isinstance(fallback, str):
        fallback = (fallback,)
    nomes.extend(fallback or ())
    vistos = set()
    for nome in nomes:
        if not nome or nome in vistos:
            continue
        vistos.add(nome)
        try:
            return registry.get(nome), nome
        except (KeyError, AttributeError, TypeError):
            continue
    return None, None


def provider_disponivel(registry, nome):
    """Indica disponibilidade sem lançar KeyError para configuração opcional."""
    selected, _ = selecionar_provider(registry, nome, ())
    return selected is not None


def obter_provider_seguro(registry, provider=None, fallback=("gemini",)):
    """Variante conveniente que devolve apenas o provider."""
    selected, _ = selecionar_provider(registry, provider, fallback)
    return selected


# Nomes verbosos/ingleses facilitam integração sem quebrar a API portuguesa.
weekly_summary = resumir_semana
fatigue_signals = calcular_sinais_fadiga
evaluate_recommendation = avaliar_resultado_recomendacao
select_provider = obter_provider_seguro
