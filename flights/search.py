from typing import Any

import requests


SERPAPI_URL = "https://serpapi.com/search.json"


def search_flights(
    api_key: str,
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
    currency: str = "USD",
    max_stops: int | None = None,
) -> dict:
    params = {
        "api_key": api_key,
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": currency,
        "type": "1" if return_date else "2",
    }
    if return_date:
        params["return_date"] = return_date
    if max_stops is not None:
        params["stops"] = str(max_stops + 1)
    params["deep_search"] = "true"

    resp = requests.get(SERPAPI_URL, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def extract_flights(data: dict) -> list[dict]:
    """Pull only the fields an LLM (or UI) actually needs."""
    results = []
    all_itineraries = (data.get("best_flights") or []) + (
        data.get("other_flights") or []
    )

    for itin in all_itineraries:
        legs = itin.get("flights") or []
        if not legs:
            continue

        segments = []
        airlines_seen = []
        flight_numbers = []

        for leg in legs:
            dep_apt = leg.get("departure_airport", {})
            arr_apt = leg.get("arrival_airport", {})
            airline = leg.get("airline", "")
            if airline and airline not in airlines_seen:
                airlines_seen.append(airline)

            segments.append({
                "airline": airline,
                "flight_number": leg.get("flight_number", ""),
                "airplane": leg.get("airplane", ""),
                "travel_class": leg.get("travel_class", ""),
                "departure_id": dep_apt.get("id", ""),
                "departure_name": dep_apt.get("name", ""),
                "departure_time": dep_apt.get("time", ""),
                "arrival_id": arr_apt.get("id", ""),
                "arrival_name": arr_apt.get("name", ""),
                "arrival_time": arr_apt.get("time", ""),
                "duration_min": leg.get("duration", 0),
                "legroom": leg.get("legroom", ""),
            })
            flight_numbers.append(leg.get("flight_number", ""))

        layovers = [
            {
                "airport": lo.get("name", ""),
                "id": lo.get("id", ""),
                "duration_min": lo.get("duration", 0),
                "overnight": lo.get("overnight", False),
            }
            for lo in (itin.get("layovers") or [])
        ]

        results.append({
            "price": itin.get("price"),
            "currency": data.get("search_parameters", {}).get("currency", "USD"),
            "trip_type": itin.get("type", ""),
            "total_duration_min": itin.get("total_duration", 0),
            "stops": len(layovers),
            "airlines": airlines_seen,
            "flight_numbers": flight_numbers,
            "segments": segments,
            "layovers": layovers,
            "extensions": itin.get("extensions", []),
            "booking_token": itin.get("booking_token", ""),
            "departure_token": itin.get("departure_token", ""),
        })

    results.sort(key=lambda x: (x["price"] or 9999))
    return results


def _fmt_duration(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h}h{m:02d}m"


def format_flights_for_llm(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    flights: list[dict],
    max_results: int = 10,
    google_flights_url: str = "",
) -> str:
    """Produce a compact, token-efficient text block an LLM can reason over."""
    if not flights:
        return f"No flights found for {departure_id} → {arrival_id} on {outbound_date}."

    header = (
        f"Flight options {departure_id} → {arrival_id} on {outbound_date} "
        f"({flights[0].get('trip_type', 'One way')}, "
        f"{flights[0].get('currency', 'USD')}):\n"
    )

    lines = [header]
    for i, fl in enumerate(flights[:max_results], 1):
        nums = "+".join(fl["flight_numbers"])
        airlines = "/".join(fl["airlines"])
        stops = f"{fl['stops']} stop{'s' if fl['stops'] != 1 else ''}" if fl["stops"] else "nonstop"

        first_seg = fl["segments"][0]
        last_seg = fl["segments"][-1]
        dep_time = first_seg["departure_time"].split(" ", 1)[-1] if " " in first_seg["departure_time"] else first_seg["departure_time"]
        arr_time = last_seg["arrival_time"].split(" ", 1)[-1] if " " in last_seg["arrival_time"] else last_seg["arrival_time"]

        route_ids = " → ".join(
            [first_seg["departure_id"]]
            + [lo["id"] for lo in fl["layovers"]]
            + [last_seg["arrival_id"]]
        )

        layover_info = ""
        if fl["layovers"]:
            parts = []
            for lo in fl["layovers"]:
                txt = f"{lo['id']} {_fmt_duration(lo['duration_min'])}"
                if lo["overnight"]:
                    txt += " overnight"
                parts.append(txt)
            layover_info = f" (layovers: {', '.join(parts)})"

        lines.append(
            f"{i}. {airlines} {nums} | {dep_time}–{arr_time} | "
            f"{route_ids} | {_fmt_duration(fl['total_duration_min'])} | "
            f"{stops}{layover_info} | ${fl['price']}"
        )

    price_lo = flights[0]["price"]
    price_hi = flights[min(max_results, len(flights)) - 1]["price"]
    lines.append(f"\nPrice range shown: ${price_lo}–${price_hi}")
    if google_flights_url:
        lines.append(f"View all flights on Google Flights: {google_flights_url}")
    return "\n".join(lines)


def fetch_flights(
    api_key: str,
    departure_code: str,
    arrival_code: str,
    start_date: str,
    return_date: str | None = None,
    max_stops: int | None = None,
) -> tuple[list[dict], str, str]:
    """Search, extract, and format flights. Returns (flights, summary, google_flights_url)."""
    data = search_flights(
        api_key, departure_code, arrival_code, start_date,
        return_date=return_date, max_stops=max_stops,
    )
    google_flights_url = data.get("search_metadata", {}).get("google_flights_url", "")
    flights = extract_flights(data)
    summary = format_flights_for_llm(
        departure_code, arrival_code, start_date, flights,
        google_flights_url=google_flights_url,
    )
    return flights, summary, google_flights_url


def resolve_flight_link(
    api_key: str,
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    booking_token: str = "",
    departure_token: str = "",
    return_date: str | None = None,
    currency: str = "USD",
) -> str:
    """Call SerpApi with a booking/departure token and return the per-flight google_flights_url."""
    token_key = ""
    token_val = ""
    if booking_token:
        token_key, token_val = "booking_token", booking_token
    elif departure_token:
        token_key, token_val = "departure_token", departure_token
    else:
        return ""

    params: dict[str, Any] = {
        "api_key": api_key,
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": currency,
        "type": "1" if return_date else "2",
        "deep_search": "true",
        token_key: token_val,
    }
    if return_date:
        params["return_date"] = return_date
    try:
        resp = requests.get(SERPAPI_URL, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json().get("search_metadata", {}).get("google_flights_url", "")
    except requests.exceptions.RequestException:
        return ""
