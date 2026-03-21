"""
For each flight itinerary found by SerpApi, get the Google Flights link
that shows that specific flight's details/booking page.

Flow:
  1. Search flights -> collect booking_tokens from each itinerary
  2. For each token, call SerpApi again -> grab search_metadata.google_flights_url
  3. Print: one-line flight summary + Google Flights link
"""

import os
from typing import Any

import requests
from dotenv import load_dotenv


SERPAPI_URL = "https://serpapi.com/search.json"


def _fmt_duration(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h}h{m:02d}m"


def _extract_itineraries(data: dict) -> list[dict]:
    """Pull itineraries (best + other) with their booking_token."""
    results: list[dict] = []
    for group in ("best_flights", "other_flights"):
        for it in data.get(group) or []:
            token = it.get("booking_token") or ""
            if not token:
                continue

            flights = it.get("flights") or []
            if not flights:
                continue

            airlines = []
            flight_nums = []
            route_ids = [flights[0].get("departure_airport", {}).get("id", "")]
            for seg in flights:
                al = seg.get("airline", "")
                if al and al not in airlines:
                    airlines.append(al)
                flight_nums.append(seg.get("flight_number", ""))
                route_ids.append(seg.get("arrival_airport", {}).get("id", ""))

            dep_time = flights[0].get("departure_airport", {}).get("time", "")
            arr_time = flights[-1].get("arrival_airport", {}).get("time", "")
            dep_short = dep_time.split(" ")[-1] if " " in dep_time else dep_time
            arr_short = arr_time.split(" ")[-1] if " " in arr_time else arr_time

            total_dur = it.get("total_duration", 0)
            price = it.get("price", 0)
            stops = len(flights) - 1

            summary = (
                f"{'/'.join(airlines)} {'+'.join(flight_nums)} | "
                f"{' -> '.join(route_ids)} | "
                f"{dep_short}-{arr_short} | "
                f"{_fmt_duration(total_dur)} | "
                f"{'nonstop' if stops == 0 else f'{stops} stop(s)'} | "
                f"${price}"
            )
            results.append({"summary": summary, "token": token, "price": price})

    results.sort(key=lambda x: x["price"])
    return results


def get_flight_link(api_key: str, params_base: dict[str, Any], token: str) -> str:
    """Call SerpApi with booking_token and return the google_flights_url."""
    params = {**params_base, "booking_token": token}
    try:
        resp = requests.get(SERPAPI_URL, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data.get("search_metadata", {}).get("google_flights_url", "(no url)")
    except requests.exceptions.RequestException as e:
        return f"(failed: {e})"


def main() -> None:
    load_dotenv()
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise SystemExit("Missing SERPAPI_KEY in .env")

    # --- Edit these ---
    departure_id = "CDG"
    arrival_id = "AUS"
    outbound_date = "2026-05-03"
    return_date = None  # YYYY-MM-DD for round trip, None for one-way
    max_links = 3       # how many flights to resolve (each costs 1 API call)
    # ------------------

    trip_type = "1" if return_date else "2"

    search_params: dict[str, Any] = {
        "api_key": api_key,
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": "USD",
        "type": trip_type,
        "deep_search": "true",
    }
    if return_date:
        search_params["return_date"] = return_date

    # Step 1: search flights
    print(f"Searching flights {departure_id} -> {arrival_id} on {outbound_date}...")
    resp = requests.get(SERPAPI_URL, params=search_params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    search_url = data.get("search_metadata", {}).get("google_flights_url", "")
    itineraries = _extract_itineraries(data)
    print(f"Found {len(itineraries)} itineraries with booking_token.\n")

    if not itineraries:
        print("No booking_tokens found. Cannot get per-flight links.")
        if search_url:
            print(f"General search: {search_url}")
        return

    # Step 2: for each itinerary, get the per-flight Google Flights link
    resolve_count = min(max_links, len(itineraries))
    print(f"Getting Google Flights links for top {resolve_count} (by price)...\n")

    for i, it in enumerate(itineraries[:resolve_count], 1):
        link = get_flight_link(api_key, search_params, it["token"])
        print(f"{i}. {it['summary']}")
        print(f"   {link}\n")

    if search_url:
        print(f"View all flights: {search_url}")


if __name__ == "__main__":
    main()
