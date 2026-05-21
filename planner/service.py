import json
from urllib.parse import quote

from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def collect_request() -> dict:
    stops_input = input("Max stops (0=nonstop, 1=1 stop, 2=2 stops, Enter=any): ").strip()
    max_stops = int(stops_input) if stops_input in ("0", "1", "2") else None

    return {
        "start_city": input("Where are you flying from? (city): ").strip(),
        "destination": input("Where are you going to? (city): ").strip(),
        "start_date": input("Start date (YYYY-MM-DD): ").strip(),
        "return_date": input("Return date (YYYY-MM-DD, Enter=one way): ").strip() or None,
        "estimated_budget": input("Estimated budget (e.g. 500 USD): ").strip(),
        "max_stops": max_stops,
    }


_airport_cache: dict[str, str] = {}


def resolve_airport_code(client, city: str) -> str:
    """Ask the LLM for the main IATA airport code of a city."""
    key = city.strip().lower()
    if key in _airport_cache:
        return _airport_cache[key]

    text = client.complete(
        system="Reply with ONLY the 3-letter IATA airport code for the main international airport of the given city. No explanation, no punctuation, just the code.",
        user=city,
        temperature=0,
        max_tokens=10,
    )
    code = text.strip().upper()[:3]
    _airport_cache[key] = code
    return code


def _parse_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise ValueError(f"Model did not return valid JSON:\n{text}")


def _google_maps_url(location_name: str, destination: str) -> str:
    query = quote(f"{location_name} {destination}", safe="")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def _enrich_locations(results: dict, destination: str) -> None:
    for location in results.get("locations", []):
        if not isinstance(location, dict):
            continue

        name = location.get("name", "").strip()
        if name and not location.get("map_url"):
            location["map_url"] = _google_maps_url(name, destination)


def _limit_locations(results: dict, limit: int = 8) -> None:
    locations = results.get("locations", [])
    if not isinstance(locations, list):
        results["locations"] = []
        return

    results["locations"] = [
        location
        for location in locations
        if isinstance(location, dict)
    ][:limit]


def get_recommendations(
    client,
    *,
    destination: str,
    start_date: str,
    return_date: str,
    estimated_budget: str,
    flight_data: str = "",
) -> dict:
    flight_section = ""
    if flight_data:
        flight_section = f"Available flights:\n{flight_data}"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        destination=destination,
        start_date=start_date,
        return_date=return_date,
        estimated_budget=estimated_budget,
        flight_section=flight_section,
    )

    text = client.complete(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        temperature=0.7,
        max_tokens=2000,
        json_format=True,
    )
    results = _parse_json(text)
    if not flight_data:
        results["recommended_flights"] = []
    _enrich_locations(results, destination)
    _limit_locations(results)
    return results
