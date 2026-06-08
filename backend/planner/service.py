import json
from urllib.parse import quote

from .prompts import (
    HOTEL_PROMPT_TEMPLATE,
    HOTEL_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)


def collect_request() -> dict:
    stops_input = input("Max stops (0=nonstop, 1=1 stop, 2=2 stops, Enter=any): ").strip()
    max_stops = int(stops_input) if stops_input in ("0", "1", "2") else None

    return {
        "start_city": input("Where are you flying from? (city): ").strip(),
        "destination": input("Where are you going to? (city): ").strip(),
        "start_date": input("Start date (YYYY-MM-DD): ").strip(),
        "return_date": input("Return date (YYYY-MM-DD, Enter=one way): ").strip() or None,
        "estimated_budget": input("Estimated budget (e.g. 500 USD, Enter=none): ").strip() or None,
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


def _format_locations_for_hotels(locations: list[dict]) -> str:
    lines = []
    for i, location in enumerate(locations, 1):
        if not isinstance(location, dict):
            continue
        name = location.get("name", "").strip()
        why = location.get("why", "").strip()
        if name:
            lines.append(f"{i}. {name}" + (f" - {why}" if why else ""))
    return "\n".join(lines) or "No specific locations provided."


def _hotel_class(hotel: dict) -> str:
    if hotel.get("hotel_class"):
        return str(hotel["hotel_class"])
    stars = hotel.get("extracted_hotel_class")
    if stars:
        return f"{stars}-star hotel"
    return ""


def _hotel_candidate_details(hotels: list[dict], max_results: int = 12) -> str:
    lines = []
    for i, hotel in enumerate(hotels[:max_results], 1):
        lines.append(
            "\n".join([
                f"{i}. {hotel.get('name', '')}",
                f"   price_per_night: {hotel.get('price_per_night', '')}",
                f"   total_price: {hotel.get('total_price', '')}",
                f"   hotel_class: {_hotel_class(hotel)}",
                f"   rating: {hotel.get('overall_rating')}",
                f"   reviews: {hotel.get('reviews')}",
                f"   address: {hotel.get('address', '')}",
                f"   location_rating: {hotel.get('location_rating')}",
                f"   services: {', '.join((hotel.get('services') or [])[:12])}",
                f"   review_summary: {'; '.join((hotel.get('review_summary') or [])[:4])}",
                f"   nearby_summary: {'; '.join((hotel.get('nearby_summary') or [])[:4])}",
                f"   nearby_places: {json.dumps(hotel.get('nearby_places') or [], ensure_ascii=False)[:700]}",
                f"   property_link: {hotel.get('property_link', '')}",
            ])
        )
    return "\n".join(lines)


def _enrich_hotel_recommendations(results: dict, hotels: list[dict]) -> None:
    hotel_by_index = {i: hotel for i, hotel in enumerate(hotels, 1)}
    cleaned = []

    for rec in results.get("recommended_hotels", []):
        if not isinstance(rec, dict):
            continue
        try:
            hotel_index = int(rec.get("hotel_index"))
        except (TypeError, ValueError):
            continue
        rec["hotel_index"] = hotel_index
        hotel = hotel_by_index.get(hotel_index)
        if not hotel:
            continue

        rec["name"] = hotel.get("name", rec.get("name", ""))
        rec["price_per_night"] = hotel.get("price_per_night", rec.get("price_per_night", ""))
        rec["total_price"] = hotel.get("total_price", rec.get("total_price", ""))
        rec["hotel_class"] = _hotel_class(hotel) or rec.get("hotel_class", "")
        rec["rating"] = hotel.get("overall_rating", rec.get("rating"))
        rec["reviews"] = hotel.get("reviews", rec.get("reviews"))
        rec["address"] = hotel.get("address", rec.get("address", ""))
        rec["location_rating"] = hotel.get("location_rating", rec.get("location_rating"))
        rec["property_link"] = hotel.get("property_link", rec.get("property_link", ""))
        if not isinstance(rec.get("services"), list):
            rec["services"] = []
        if not rec.get("services"):
            rec["services"] = (hotel.get("services") or [])[:12]
        if not isinstance(rec.get("review_summary"), list):
            rec["review_summary"] = []
        if not rec.get("review_summary"):
            rec["review_summary"] = (hotel.get("review_summary") or [])[:4]
        if not isinstance(rec.get("nearby_summary"), list):
            rec["nearby_summary"] = []
        if not rec.get("nearby_summary"):
            rec["nearby_summary"] = (hotel.get("nearby_summary") or [])[:4]
        cleaned.append(rec)

    results["recommended_hotels"] = cleaned[:5]


def get_recommendations(
    client,
    *,
    destination: str,
    start_date: str,
    return_date: str,
    estimated_budget: str | None,
    flight_data: str = "",
    retrieved_context: str = "",
) -> dict:
    flight_section = ""
    if flight_data:
        flight_section = f"Available flights:\n{flight_data}"
    budget_text = (estimated_budget or "").strip() or "No activity budget specified"
    retrieved_context_section = ""
    if retrieved_context.strip():
        retrieved_context_section = f"\n{retrieved_context.strip()}\n"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        destination=destination,
        start_date=start_date,
        return_date=return_date,
        estimated_budget=budget_text,
        flight_section=flight_section,
        retrieved_context_section=retrieved_context_section,
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


def get_hotel_recommendations(
    client,
    *,
    destination: str,
    locations: list[dict],
    hotels: list[dict],
) -> list[dict]:
    if not hotels:
        return []

    user_prompt = HOTEL_PROMPT_TEMPLATE.format(
        destination=destination,
        locations_section=_format_locations_for_hotels(locations),
        hotel_section=_hotel_candidate_details(hotels),
    )

    text = client.complete(
        system=HOTEL_SYSTEM_PROMPT,
        user=user_prompt,
        temperature=0.4,
        max_tokens=2000,
        json_format=True,
    )
    results = _parse_json(text)
    _enrich_hotel_recommendations(results, hotels)
    return results.get("recommended_hotels", [])
