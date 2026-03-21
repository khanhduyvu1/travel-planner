import os
from dotenv import load_dotenv

from flights import fetch_flights
from planner import (
    get_client, collect_request, resolve_airport_code,
    get_recommendations, render_text, save_text, save_json,
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
    serpapi_key = os.getenv("SERPAPI_KEY")

    if serpapi_key:
        flights, flight_summary, google_flights_url = fetch_flights(
            serpapi_key, departure_code, arrival_code,
            req["start_date"], req["return_date"], req["max_stops"],
        )
        save_json("flights.json", flights)
        save_text("flights.txt", flight_summary)

    results = get_recommendations(
        client,
        destination=req["destination"],
        start_date=req["start_date"],
        return_date=req["return_date"],
        estimated_budget=req["estimated_budget"],
        flight_data=flight_summary,
    )

    if google_flights_url:
        results["all_flights_link"] = google_flights_url

    save_text("recommendations.txt", render_text(results))
    save_json("recommendations.json", results)
    print("Done. See flights.txt, flights.json, recommendations.txt, recommendations.json")


if __name__ == "__main__":
    main()
