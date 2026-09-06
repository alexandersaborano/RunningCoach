"""Dependency-free analytics helpers for training history.

The functions in this module deliberately accept the dictionaries already used
by the application (Portuguese and Intervals.icu field names are supported).
"""

from __future__ import annotations

import csv
import io
import json
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any, Iterable, Mapping


def _number(item: Mapping[str, Any], *keys: str) -> float:
    for key in keys:
        value = item.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass
    return 0.0


def _day(item: Mapping[str, Any]) -> date | None:
    value = next((item.get(k) for k in ("date", "data", "start_date", "start_date_local") if item.get(k)), None)
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if value:
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
        except ValueError:
            try:
                return date.fromisoformat(str(value)[:10])
            except ValueError:
                return None
    return None


def _metrics(items: list[Mapping[str, Any]]) -> dict[str, Any]:
    distance = sum(
        _number(x, "distance_km", "distancia_km") if ("distance_km" in x or "distancia_km" in x)
        else _number(x, "distance") / 1000 for x in items
    )
    duration = sum(
        _number(x, "tempo_movimento_min", "duration_min") if ("tempo_movimento_min" in x or "duration_min" in x)
        else _number(x, "moving_time") / 60 for x in items
    )
    load = sum(_number(x, "carga_tss", "icu_training_load", "training_load", "load") for x in items)
    return {
        "session_count": len(items),
        "distance_km": round(distance, 2),
        "duration_min": round(duration, 2),
        "load": round(load, 2),
        "average_pace_min_km": round(duration / distance, 2) if distance else None,
        "average_heartrate": round(sum(_number(x, "fc_media", "average_heartrate", "average_hr") for x in items) / len(items), 2) if items else None,
    }


def classify_intensity(session: Mapping[str, Any], zones: Iterable[float] | None = None) -> str:
    """Return ``easy``, ``moderate``, ``hard`` or ``unknown``."""
    explicit = session.get("intensity") or session.get("intensidade")
    if explicit:
        return str(explicit).strip().lower()
    hr = _number(session, "fc_media", "average_heartrate", "average_hr")
    if not hr:
        return "unknown"
    limits = sorted(float(x) for x in (zones or (140, 160)))
    if hr < limits[0]:
        return "easy"
    if hr < limits[-1]:
        return "moderate"
    return "hard"


def aggregate_weekly(sessions: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate sessions into ISO weeks beginning on Monday."""
    weeks: dict[date, list[Mapping[str, Any]]] = {}
    for session in sessions:
        day = _day(session)
        if day:
            monday = day - timedelta(days=day.weekday())
            weeks.setdefault(monday, []).append(session)
    result = []
    for monday in sorted(weeks):
        row = {"week_start": monday.isoformat(), **_metrics(weeks[monday])}
        row["intensity_counts"] = dict(Counter(classify_intensity(x) for x in weeks[monday]))
        result.append(row)
    return result


def compare_equivalent_periods(current: Iterable[Mapping[str, Any]], previous: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Compare two already-selected, equivalent periods and report deltas."""
    now, before = _metrics(list(current)), _metrics(list(previous))
    delta = {}
    for key in ("session_count", "distance_km", "duration_min", "load", "average_pace_min_km", "average_heartrate"):
        if now[key] is not None and before[key] is not None:
            delta[key] = round(now[key] - before[key], 2)
    return {"current": now, "previous": before, "delta": delta}


def filter_sessions(
    sessions: Iterable[Mapping[str, Any]], *, start: Any = None, end: Any = None,
    workout_type: str | Iterable[str] | None = None, intensity: str | Iterable[str] | None = None,
    recovery: str | Iterable[str] | None = None,
) -> list[Mapping[str, Any]]:
    """Filter history without mutating the source records."""
    start_day = _day({"date": start}) if start else None
    end_day = _day({"date": end}) if end else None
    def matches(value: Any, wanted: Any) -> bool:
        if wanted is None:
            return True
        values = {str(x).lower() for x in wanted} if isinstance(wanted, (list, tuple, set, frozenset)) else {str(wanted).lower()}
        return str(value or "").lower() in values
    result = []
    for item in sessions:
        day = _day(item)
        kind = item.get("type") or item.get("workout_type") or item.get("tipo")
        state = item.get("recovery_status") or item.get("estado_recuperacao") or item.get("recovery")
        if ((start_day and (not day or day < start_day)) or (end_day and (not day or day > end_day))
                or not matches(kind, workout_type) or not matches(classify_intensity(item), intensity)
                or not matches(state, recovery)):
            continue
        result.append(item)
    return result


def consolidated_export_data(sessions: Iterable[Mapping[str, Any]], analyses: Iterable[Mapping[str, Any]] = (),
                             feedback: Iterable[Mapping[str, Any]] = (), planned: Iterable[Mapping[str, Any]] = ()) -> list[dict[str, Any]]:
    """Produce flat, JSON/CSV-friendly records from all local history sources."""
    rows = []
    for source, values in (("completed", sessions), ("planned", planned), ("analysis", analyses), ("feedback", feedback)):
        for item in values or ():
            row = {str(k): v for k, v in dict(item).items() if isinstance(v, (str, int, float, bool, type(None)))}
            row["record_type"] = source
            rows.append(row)
    return rows


def export_json(records: Iterable[Mapping[str, Any]]) -> str:
    return json.dumps(list(records), ensure_ascii=False, indent=2, default=str)


def export_csv(records: Iterable[Mapping[str, Any]]) -> str:
    rows = list(records)
    fields = sorted({key for row in rows for key in row})
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


# Concise aliases useful to callers migrating from Portuguese UI code.
weekly_aggregation = aggregate_weekly
equivalent_period_comparison = compare_equivalent_periods
advanced_filter = filter_sessions
