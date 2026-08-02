from typing import Any
from urllib.parse import quote

import requests


SERPAPI_URL = "https://serpapi.com/search.json"


def search_restaurants(
    api_key: str,
    query: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict:
    params: dict[str, Any] = {
        "api_key": api_key,
        "engine": "google_maps",
        "q": query,
        "type": "search",
        "hl": "en",
    }
    if latitude is not None and longitude is not None:
        params["ll"] = f"@{latitude},{longitude},15z"

    resp = requests.get(SERPAPI_URL, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _google_maps_url(name: str, destination: str) -> str:
    query = quote(f"{name} {destination}", safe="")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def extract_restaurants(data: dict) -> list[dict]:
    results = []
    places = (data.get("local_results") or data.get("places") or data.get("results") or [])

    for place in places:
        name = _text(place.get("title")).strip()
        if not name:
            continue

        gps = place.get("gps_coordinates") or {}
        results.append({
            "name": name,
            "address": _text(place.get("address")),
            "rating": place.get("rating"),
            "reviews": place.get("reviews"),
            "price": _text(place.get("price")),
            "type": _text(place.get("type")),
            "phone": _text(place.get("phone")),
            "website": _text(place.get("website")),
            "thumbnail": _text(place.get("thumbnail")),
            "latitude": gps.get("latitude"),
            "longitude": gps.get("longitude"),
            "map_url": _google_maps_url(name, _text(place.get("address"))),
        })

    return results


def format_restaurants_for_llm(restaurants: list[dict], max_results: int = 10) -> str:
    if not restaurants:
        return ""

    lines = [f"Restaurant candidates ({len(restaurants)} found):"]
    for i, r in enumerate(restaurants[:max_results], 1):
        rating = r.get("rating")
        reviews = r.get("reviews")
        rating_text = f"{rating}/5 ({reviews} reviews)" if rating else "rating unavailable"
        price = r.get("price") or "price unavailable"
        addr = r.get("address") or "address unavailable"

        lines.append(
            f"{i}. {r.get('name', '')} | {rating_text} | {price} | "
            f"{addr} | type: {r.get('type', '')}"
        )

    return "\n".join(lines)


def fetch_restaurants(
    api_key: str,
    destination: str,
    location_name: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> tuple[list[dict], str]:
    query = f"restaurants near {location_name} {destination}"
    data = search_restaurants(api_key, query, latitude, longitude)
    restaurants = extract_restaurants(data)
    summary = format_restaurants_for_llm(restaurants)
    return restaurants, summary