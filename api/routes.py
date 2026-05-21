import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from flights import fetch_flights
from AI_model import get_client
from planner import resolve_airport_code, get_recommendations, render_text, save_json, save_text

load_dotenv()

from .schemas import (
    FlightSearchRequest, FlightSearchResponse,
    RecommendationRequest, RecommendationResponse,
)

router = APIRouter(prefix="/api")


@router.post("/flights", response_model=FlightSearchResponse)
def search_flights_endpoint(req: FlightSearchRequest):
    """Search flights by airport codes. SerpAPI only, no AI."""
    serpapi_key = os.getenv("SERPAPI_KEY")
    if not serpapi_key:
        raise HTTPException(status_code=500, detail="SERPAPI_KEY not configured")

    try:
        flights, flight_summary, google_flights_url = fetch_flights(
            serpapi_key, req.departure_code.upper(), req.arrival_code.upper(),
            req.start_date, req.return_date, req.max_stops,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Flight search failed: {exc}")

    return FlightSearchResponse(
        departure_code=req.departure_code.upper(),
        arrival_code=req.arrival_code.upper(),
        flights=flights,
        flight_summary=flight_summary,
        google_flights_url=google_flights_url,
    )


@router.post("/recommendations", response_model=RecommendationResponse)
def get_recs(req: RecommendationRequest):
    """Full pipeline: resolve airports (AI) + search flights (SerpAPI) + recommendations (AI)."""
    client = get_client(req.model_mode)

    try:
        departure_code = resolve_airport_code(client, req.start_city)
        arrival_code = resolve_airport_code(client, req.destination)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to resolve airport codes: {exc}")

    flights = []
    flight_summary = ""
    google_flights_url = ""
    serpapi_key = os.getenv("SERPAPI_KEY")

    if serpapi_key:
        try:
            flights, flight_summary, google_flights_url = fetch_flights(
                serpapi_key, departure_code, arrival_code,
                req.start_date, req.return_date, req.max_stops,
            )
            save_json("flights.json", flights)
            save_text("flights.txt", flight_summary)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Flight search failed: {exc}")

    try:
        recs = get_recommendations(
            client,
            destination=req.destination,
            start_date=req.start_date,
            return_date=req.return_date,
            estimated_budget=req.estimated_budget,
            flight_data=flight_summary,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Recommendation generation failed: {exc}")

    recommended_flights = recs.get("recommended_flights", [])
    if not flight_summary:
        recommended_flights = []

    if google_flights_url:
        recs["all_flights_link"] = google_flights_url
    recs["model_info"] = client.info()

    recommendations_text = render_text(recs)
    save_text("recommendations.txt", recommendations_text)

    return RecommendationResponse(
        departure_code=departure_code,
        arrival_code=arrival_code,
        destination=recs.get("destination", req.destination),
        google_flights_url=google_flights_url,
        flights=flights,
        recommended_flights=recommended_flights,
        locations=recs.get("locations", []),
        total_estimated_budget=recs.get("total_estimated_budget", 0),
        model_info=recs.get("model_info"),
        recommendations_text=recommendations_text,
    )
