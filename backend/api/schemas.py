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
    estimated_budget: str | None = Field(None, examples=["1000 USD"])
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


class HotelOption(BaseModel):
    name: str
    description: str = ""
    address: str = ""
    hotel_class: str = ""
    extracted_hotel_class: int | None = None
    overall_rating: int | float | None = None
    reviews: int | None = None
    location_rating: int | float | None = None
    price_per_night: str = ""
    extracted_price_per_night: int | float | None = None
    total_price: str = ""
    extracted_total_price: int | float | None = None
    services: list[str] = []
    review_summary: list[str] = []
    nearby_summary: list[str] = []
    nearby_places: list[dict] = []
    latitude: int | float | None = None
    longitude: int | float | None = None
    thumbnail: str = ""
    property_token: str = ""
    property_link: str = ""


class RecommendedHotel(BaseModel):
    hotel_index: int
    name: str
    summary: str = ""
    price_per_night: str = ""
    total_price: str = ""
    hotel_class: str = ""
    rating: int | float | None = None
    reviews: int | None = None
    quality_reason: str = ""
    proximity_reason: str = ""
    services: list[str] = []
    review_summary: list[str] = []
    nearby_summary: list[str] = []
    address: str = ""
    location_rating: int | float | None = None
    property_link: str = ""


class Location(BaseModel):
    name: str
    details: str = ""
    why: str
    things_to_do: list[str] = []
    suggested_days: int | float = 1
    map_url: str | None = None


class ModelInfo(BaseModel):
    provider: str = ""
    backend: str = ""
    model: str = ""
    api_base: str | None = None
    timeout_seconds: int | None = None


class RecommendationResponse(BaseModel):
    departure_code: str
    arrival_code: str
    destination: str
    google_flights_url: str = ""
    flights: list[FlightOption] = []
    recommended_flights: list[RecommendedFlight] = []
    hotels: list[HotelOption] = []
    recommended_hotels: list[RecommendedHotel] = []
    locations: list[Location] = []
    total_estimated_budget: int | float = 0
    rag_context_used: str = ""
    model_info: ModelInfo | None = None
    recommendations_text: str = ""
