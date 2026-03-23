from __future__ import annotations

from pydantic import BaseModel, Field


# --- Request schemas ---

class FlightSearchRequest(BaseModel):
    departure_code: str = Field(..., min_length=3, max_length=3, examples=["TPA"])
    arrival_code: str = Field(..., min_length=3, max_length=3, examples=["HAN"])
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-05-30"])
    return_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-06-30"])
    max_stops: int | None = Field(None, ge=0, le=2)


class RecommendationRequest(BaseModel):
    start_city: str = Field(..., min_length=1, examples=["Tampa"])
    destination: str = Field(..., min_length=1, examples=["Hanoi"])
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-05-30"])
    return_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-06-30"])
    estimated_budget: str = Field(..., min_length=1, examples=["1000 USD"])
    max_stops: int | None = Field(None, ge=0, le=2)


# --- Response schemas ---

class FlightSegment(BaseModel):
    airline: str = ""
    flight_number: str = ""
    departure_id: str = ""
    arrival_id: str = ""
    departure_time: str = ""
    arrival_time: str = ""
    duration_min: int = 0


class FlightOption(BaseModel):
    price: int | None = None
    currency: str = "USD"
    total_duration_min: int = 0
    stops: int = 0
    airlines: list[str] = []
    flight_numbers: list[str] = []
    segments: list[FlightSegment] = []


class FlightSearchResponse(BaseModel):
    departure_code: str
    arrival_code: str
    flights: list[FlightOption] = []
    flight_summary: str = ""
    google_flights_url: str = ""


class RecommendedFlight(BaseModel):
    flight_index: int
    summary: str
    reason: str


class Location(BaseModel):
    name: str
    why: str
    things_to_do: list[str] = []
    suggested_days: int = 1


class RecommendationResponse(BaseModel):
    departure_code: str
    arrival_code: str
    destination: str
    google_flights_url: str = ""
    recommended_flights: list[RecommendedFlight] = []
    locations: list[Location] = []
    total_estimated_budget: int | float = 0
    recommendations_text: str = ""
