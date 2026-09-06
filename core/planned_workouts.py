"""Validated local persistence for manually planned workouts."""

from __future__ import annotations

import json
import uuid
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping


class PlannedWorkoutError(ValueError):
    """Raised when a planned workout is invalid."""


def validate_workout(workout: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(workout, Mapping):
        raise PlannedWorkoutError("workout must be an object")
    result = dict(workout)
    workout_date = result.get("date") or result.get("data")
    if not workout_date:
        raise PlannedWorkoutError("date is required")
    try:
        date.fromisoformat(str(workout_date)[:10])
    except ValueError as exc:
        raise PlannedWorkoutError("date must be ISO formatted (YYYY-MM-DD)") from exc
    result["date"] = str(workout_date)[:10]
    if not (result.get("name") or result.get("nome") or result.get("title")):
        raise PlannedWorkoutError("name is required")
    for field in ("duration_min", "distance_km"):
        if field in result and result[field] is not None:
            try:
                if float(result[field]) < 0:
                    raise ValueError
                result[field] = float(result[field])
            except (TypeError, ValueError) as exc:
                raise PlannedWorkoutError(f"{field} must be non-negative") from exc
    result.setdefault("status", "planned")
    result.setdefault("workout_type", result.get("type") or result.get("tipo") or "other")
    return result


class PlannedWorkoutStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PlannedWorkoutError("invalid planned workouts file") from exc
        return list(data.get("workouts", [])) if isinstance(data, dict) else (data if isinstance(data, list) else [])

    def _write(self, workouts: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(workouts, ensure_ascii=False, indent=2), encoding="utf-8")

    def list(self) -> list[dict[str, Any]]:
        return self._read()

    def create(self, workout: Mapping[str, Any]) -> dict[str, Any]:
        item = validate_workout(workout)
        item.setdefault("id", uuid.uuid4().hex)
        items = self._read()
        if any(x.get("id") == item["id"] for x in items):
            raise PlannedWorkoutError("duplicate workout id")
        items.append(item)
        self._write(items)
        return item

    def get(self, workout_id: str) -> dict[str, Any] | None:
        return next((x for x in self._read() if x.get("id") == workout_id), None)

    def update(self, workout_id: str, changes: Mapping[str, Any]) -> dict[str, Any]:
        items = self._read()
        for index, item in enumerate(items):
            if item.get("id") == workout_id:
                updated = validate_workout({**item, **dict(changes), "id": workout_id})
                items[index] = updated
                self._write(items)
                return updated
        raise KeyError(workout_id)

    def delete(self, workout_id: str) -> bool:
        items = self._read()
        remaining = [x for x in items if x.get("id") != workout_id]
        if len(remaining) == len(items):
            return False
        self._write(remaining)
        return True


def merge_planned_completed(planned: Iterable[Mapping[str, Any]], completed: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return one chronologically sorted calendar, preserving all source fields."""
    rows = [{**dict(x), "source": "planned"} for x in planned]
    rows.extend({**dict(x), "source": "completed"} for x in completed)
    return sorted(rows, key=lambda x: str(x.get("date") or x.get("data") or x.get("start_date") or ""))


merge_sessions = merge_planned_completed
