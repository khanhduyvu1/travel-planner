import os
import sys
from pathlib import Path

from dotenv import load_dotenv

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.flights import fetch_flights
from backend.hotels import fetch_hotels
from backend.AI_model import get_client
from backend.rag import learn_from_locations, retrieve_context
from backend.planner import (
    collect_request, resolve_airport_code,
    get_hotel_recommendations,
    get_recommendations,
    render_text,
    save_text,
    save_json,
)


def main() -> None:
    load_dotenv()
    client = get_client()
    req = collect_request()

    departure_code = resolve_airport_code(client, req["start_city"])
    arrival_code = resolve_airport_code(client, req["destination"])
    print(f"Airports: {req['start_city']} ({departure_code}) -> {req['destination']} ({arrival_code})")

    flight_summary = ""
    google_flights_url = ""
    hotels = []
    hotel_summary = ""
    serpapi_key = os.getenv("SERPAPI_KEY")

    if serpapi_key:
        flights, flight_summary, google_flights_url = fetch_flights(
            serpapi_key, departure_code, arrival_code,
            req["start_date"], req["return_date"], req["max_stops"],
        )
        save_json("flights.json", flights)
        save_text("flights.txt", flight_summary)

    retrieved_context = retrieve_context(req["destination"])
    save_text("rag_context.txt", retrieved_context)

    results = get_recommendations(
        client,
        destination=req["destination"],
        start_date=req["start_date"],
        return_date=req["return_date"],
        estimated_budget=req["estimated_budget"],
        flight_data=flight_summary,
        retrieved_context=retrieved_context,
    )
    learn_from_locations(req["destination"], results.get("locations", []))

    if google_flights_url:
        results["all_flights_link"] = google_flights_url

    if serpapi_key:
        try:
            hotels, hotel_summary = fetch_hotels(
                serpapi_key,
                req["destination"],
                req["start_date"],
                req["return_date"],
            )
            save_json("hotels.json", hotels)
            save_text("hotels.txt", hotel_summary)
        except Exception:
            hotels = []

    results["hotels"] = hotels
    results["rag_context_used"] = retrieved_context
    results["recommended_hotels"] = get_hotel_recommendations(
        client,
        destination=req["destination"],
        locations=results.get("locations", []),
        hotels=hotels,
    ) if hotels else []
    results["model_info"] = client.info()

    save_text("recommendations.txt", render_text(results))
    save_json("recommendations.json", results)
    print(
        "Done. See backend/output/flights.txt, backend/output/flights.json, "
        "backend/output/hotels.txt, backend/output/hotels.json, "
        "backend/output/recommendations.txt, backend/output/recommendations.json"
    )


if __name__ == "__main__":
    main()
