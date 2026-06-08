from datetime import datetime, timedelta
from urllib.parse import quote

import requests


SERPAPI_URL = "https://serpapi.com/search.json"


def _checkout_date(start_date: str, return_date: str | None) -> str:
    if return_date:
        return return_date
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    return (start + timedelta(days=1)).isoformat()


def search_hotels(
    api_key: str,
    destination: str,
    check_in_date: str,
    check_out_date: str | None = None,
    currency: str = "USD",
) -> dict:
    params = {
        "api_key": api_key,
        "engine": "google_hotels",
        "q": f"Hotels in {destination}",
        "check_in_date": check_in_date,
        "check_out_date": _checkout_date(check_in_date, check_out_date),
        "currency": currency,
        "hl": "en",
        "gl": "us",
    }

    resp = requests.get(SERPAPI_URL, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _review_summary(prop: dict, limit: int = 4) -> list[str]:
    summaries = []
    for item in (prop.get("reviews_breakdown") or [])[:limit]:
        name = _text(item.get("name"))
        description = _text(item.get("description"))
        if description.strip().lower() == name.strip().lower():
            continue
        if name and description:
            summaries.append(f"{name}: {description}")
        elif name:
            summaries.append(name)
    return summaries


def _services(prop: dict) -> list[str]:
    services = []
    seen = set()
    for service in prop.get("amenities") or prop.get("hotel_amenities") or []:
        text = _text(service).strip()
        key = text.lower()
        if text and key not in seen:
            services.append(text)
            seen.add(key)
    return services


def _google_maps_url(*parts: str) -> str:
    query = quote(" ".join(part for part in parts if part).strip(), safe="")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def _nearby_summary(prop: dict, limit: int = 4) -> list[str]:
    summaries = []
    for place in (prop.get("nearby_places") or [])[:limit]:
        name = _text(place.get("name"))
        transports = place.get("transportations") or []
        durations = [
            f"{_text(t.get('type')).strip()} {_text(t.get('duration')).strip()}".strip()
            for t in transports
            if _text(t.get("duration"))
        ]
        if name:
            summaries.append(f"{name}: {', '.join(durations)}" if durations else name)
    return summaries


def extract_hotels(data: dict, destination: str = "") -> list[dict]:
    """Pull only hotel fields needed by the API, UI, and ranking prompt."""
    results = []
    properties = data.get("properties") or []

    for prop in properties:
        name = _text(prop.get("name")).strip()
        if not name:
            continue

        rate_per_night = prop.get("rate_per_night") or {}
        total_rate = prop.get("total_rate") or {}
        gps = prop.get("gps_coordinates") or {}
        address = _text(prop.get("address"))
        maps_query_location = address or destination

        results.append({
            "name": name,
            "description": _text(prop.get("description")),
            "address": address,
            "hotel_class": _text(prop.get("hotel_class")),
            "extracted_hotel_class": prop.get("extracted_hotel_class"),
            "overall_rating": prop.get("overall_rating"),
            "reviews": prop.get("reviews"),
            "location_rating": prop.get("location_rating"),
            "price_per_night": _text(rate_per_night.get("lowest")),
            "extracted_price_per_night": rate_per_night.get("extracted_lowest"),
            "total_price": _text(total_rate.get("lowest")),
            "extracted_total_price": total_rate.get("extracted_lowest"),
            "services": _services(prop),
            "review_summary": _review_summary(prop),
            "nearby_summary": _nearby_summary(prop),
            "nearby_places": prop.get("nearby_places") or [],
            "latitude": gps.get("latitude"),
            "longitude": gps.get("longitude"),
            "thumbnail": _text(prop.get("thumbnail")),
            "property_token": _text(prop.get("property_token")),
            "property_link": _google_maps_url(name, maps_query_location),
        })

    results.sort(key=lambda h: (
        h["extracted_price_per_night"] is None,
        h["extracted_price_per_night"] or 999999,
        -(h["overall_rating"] or 0),
    ))
    return results


def _fmt_hotel_class(hotel: dict) -> str:
    if hotel.get("hotel_class"):
        return str(hotel["hotel_class"])
    stars = hotel.get("extracted_hotel_class")
    if stars:
        return f"{stars}-star hotel"
    return "star class unavailable"


def _fmt_nearby_places(hotel: dict, max_places: int = 3) -> str:
    parts = []
    for place in hotel.get("nearby_places", [])[:max_places]:
        name = place.get("name", "")
        transports = place.get("transportations") or []
        durations = [
            f"{t.get('type', '').strip()} {t.get('duration', '').strip()}".strip()
            for t in transports
            if t.get("duration")
        ]
        if name:
            parts.append(f"{name} ({', '.join(durations)})" if durations else name)
    return "; ".join(parts)


def format_hotels_for_llm(hotels: list[dict], max_results: int = 12) -> str:
    """Produce compact hotel candidate text for model ranking."""
    if not hotels:
        return ""

    lines = ["Hotel candidates:"]
    for i, hotel in enumerate(hotels[:max_results], 1):
        review_summary = "; ".join((hotel.get("review_summary") or [])[:3]) or "review summary unavailable"
        services = ", ".join((hotel.get("services") or [])[:8]) or "services unavailable"
        nearby = "; ".join((hotel.get("nearby_summary") or [])[:4]) or _fmt_nearby_places(hotel) or "nearby places unavailable"
        rating = hotel.get("overall_rating")
        reviews = hotel.get("reviews")
        rating_text = f"{rating}/5 from {reviews} reviews" if rating else "rating unavailable"
        price = hotel.get("price_per_night") or "price unavailable"
        total = hotel.get("total_price") or "total price unavailable"

        lines.append(
            f"{i}. {hotel.get('name')} | {_fmt_hotel_class(hotel)} | "
            f"{rating_text} | {price} per night | {total} total | "
            f"address: {hotel.get('address') or 'address unavailable'} | "
            f"location rating: {hotel.get('location_rating') or 'unavailable'} | "
            f"reviews: {review_summary} | "
            f"services: {services} | "
            f"nearby: {nearby}"
        )

    return "\n".join(lines)


def fetch_hotels(
    api_key: str,
    destination: str,
    start_date: str,
    return_date: str | None = None,
) -> tuple[list[dict], str]:
    """Search, extract, and format hotels. Returns (hotels, hotel_summary)."""
    data = search_hotels(api_key, destination, start_date, return_date)
    hotels = extract_hotels(data, destination)
    summary = format_hotels_for_llm(hotels)
    return hotels, summary
