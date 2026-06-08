import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge_cache"


def _now() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-") or "unknown"


def _location_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.strip().lower()).strip()


def _cache_path(destination: str) -> Path:
    return KNOWLEDGE_DIR / f"{_slug(destination)}.json"


def _read_cache(destination: str) -> dict[str, Any]:
    path = _cache_path(destination)
    if not path.exists():
        return {"destination": destination, "locations": {}}

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return {"destination": destination, "locations": {}}
    if not isinstance(data.get("locations"), dict):
        data["locations"] = {}
    data.setdefault("destination", destination)
    return data


def _write_cache(destination: str, data: dict[str, Any]) -> None:
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(destination)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _normalize_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _compact_text(value: object, max_chars: int = 180) -> str:
    if not isinstance(value, str):
        return ""

    text = re.sub(r"\s+", " ", value.strip())
    if not text:
        return ""

    first_sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0].strip()
    text = first_sentence or text
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].rstrip(".,;:") + "."


def _is_similar_text(a: str, b: str) -> bool:
    a_norm = _normalize_text(a)
    b_norm = _normalize_text(b)
    if not a_norm or not b_norm:
        return False
    if a_norm == b_norm:
        return True
    if a_norm[:60] == b_norm[:60]:
        return True

    a_words = set(a_norm.split())
    b_words = set(b_norm.split())
    if not a_words or not b_words:
        return False
    overlap = len(a_words & b_words) / max(len(a_words), len(b_words))
    return overlap >= 0.72


def _append_unique(existing: list, values: list, limit: int) -> list:
    result = []

    for value in existing + values:
        text = _compact_text(value)
        if not text:
            continue
        if not any(_is_similar_text(text, current) for current in result):
            result.append(text)
        if len(result) >= limit:
            break

    return result


def _suggested_days(value: object) -> int | float | None:
    if isinstance(value, (int, float)):
        return value
    return None


def _avg_suggested_days(history: object) -> int | float | None:
    if not isinstance(history, list):
        return None
    values = [value for value in history if isinstance(value, (int, float))]
    if not values:
        return None
    avg = sum(values) / len(values)
    return round(avg, 2)


def _confidence_score(location: dict) -> float:
    count = max(int(location.get("times_recommended", 0)), 0)
    reasons = len(location.get("common_reasons") or [])
    activities = len(location.get("things_to_do") or [])
    has_map = 1 if location.get("map_url") else 0
    score = min(count / 5, 1.0) * 0.65
    score += min(reasons / 4, 1.0) * 0.18
    score += min(activities / 4, 1.0) * 0.12
    score += has_map * 0.05
    return round(min(score, 1.0), 2)


def _refresh_location_metrics(location: dict) -> None:
    location["common_reasons"] = _append_unique(location.get("common_reasons", []), [], 8)
    location["things_to_do"] = _append_unique(location.get("things_to_do", []), [], 8)
    location["avg_suggested_days"] = _avg_suggested_days(location.get("suggested_days_history"))
    location["confidence_score"] = _confidence_score(location)


def retrieve_context(destination: str, limit: int = 12) -> str:
    """Return compact learned destination context. Fail soft if cache is unavailable."""
    try:
        data = _read_cache(destination)
    except Exception:
        return ""

    locations = [
        location
        for location in data.get("locations", {}).values()
        if isinstance(location, dict) and location.get("name")
    ]
    if not locations:
        return ""

    for loc in locations:
        _refresh_location_metrics(loc)

    locations.sort(
        key=lambda loc: (
            loc.get("confidence_score", 0),
            loc.get("times_recommended", 0),
            loc.get("last_seen", ""),
        ),
        reverse=True,
    )

    lines = ["Learned destination context from previous trip plans:"]
    for loc in locations[:limit]:
        reasons = "; ".join((loc.get("common_reasons") or [])[:2])
        activities = "; ".join((loc.get("things_to_do") or [])[:3])
        avg_days = loc.get("avg_suggested_days")
        parts = [
            (
                f"- {loc.get('name')} "
                f"(confidence {loc.get('confidence_score', 0)}, "
                f"recommended {loc.get('times_recommended', 0)} times)"
            ),
        ]
        if avg_days:
            parts.append(f"avg days: {avg_days}")
        if reasons:
            parts.append(f"reasons: {reasons}")
        if activities:
            parts.append(f"activities: {activities}")
        lines.append(" | ".join(parts))

    return "\n".join(lines)


def learn_from_locations(destination: str, locations: list[dict]) -> None:
    """Merge generated locations into destination memory. Fail soft for callers."""
    try:
        data = _read_cache(destination)
        data["destination"] = destination
        cached_locations = data.setdefault("locations", {})
        today = _now()

        for location in locations:
            if not isinstance(location, dict):
                continue

            name = str(location.get("name", "")).strip()
            if not name:
                continue

            key = _location_key(name)
            if not key:
                continue

            cached = cached_locations.setdefault(key, {
                "name": name,
                "map_url": location.get("map_url") or "",
                "times_recommended": 0,
                "suggested_days_history": [],
                "common_reasons": [],
                "things_to_do": [],
                "first_seen": today,
                "last_seen": today,
            })

            cached["name"] = cached.get("name") or name
            if location.get("map_url"):
                cached["map_url"] = location["map_url"]
            cached["times_recommended"] = int(cached.get("times_recommended", 0)) + 1
            cached.setdefault("first_seen", today)
            cached["last_seen"] = today

            days = _suggested_days(location.get("suggested_days"))
            if days is not None:
                cached.setdefault("suggested_days_history", []).append(days)
                cached["suggested_days_history"] = cached["suggested_days_history"][-12:]

            cached["common_reasons"] = _append_unique(
                cached.get("common_reasons", []),
                [location.get("why", ""), location.get("details", "")],
                limit=8,
            )
            cached["things_to_do"] = _append_unique(
                cached.get("things_to_do", []),
                location.get("things_to_do", []) if isinstance(location.get("things_to_do"), list) else [],
                limit=8,
            )
            _refresh_location_metrics(cached)

        _write_cache(destination, data)
    except Exception:
        return
