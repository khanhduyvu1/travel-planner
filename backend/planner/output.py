import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def render_text(results: dict) -> str:
    dest = results.get("destination", "Unknown")
    budget = results.get("total_estimated_budget", "?")
    lines = [f"Travel Plan: {dest}", f"Total estimated budget: ${budget}", ""]

    locations = results.get("locations", [])
    if locations:
        lines.append("=" * 50)
        lines.append("PLACES TO VISIT")
        lines.append("=" * 50)
        for i, loc in enumerate(locations, 1):
            days = loc.get("suggested_days", "?")
            lines.append(f"  {i}. {loc.get('name', '?')} ({days} day{'s' if days != 1 else ''})")
            map_url = loc.get("map_url")
            if map_url:
                lines.append(f"     Map: {map_url}")
            details = loc.get("details")
            if details:
                lines.append(f"     Details: {details}")
            lines.append(f"     Why: {loc.get('why', '')}")
            things = loc.get("things_to_do", [])
            for t in things:
                lines.append(f"       - {t}")
            lines.append("")

    flights = results.get("recommended_flights", [])
    if flights:
        lines.append("=" * 50)
        lines.append("RECOMMENDED FLIGHTS")
        lines.append("=" * 50)
        for i, f in enumerate(flights, 1):
            lines.append(f"  {i}. {f.get('summary', '')}")
            lines.append(f"     Why: {f.get('reason', '')}")
        all_flights_link = results.get("all_flights_link", "")
        if all_flights_link:
            lines.append(f"\n  Browse all flights on Google Flights: {all_flights_link}")
        lines.append("")

    hotels = results.get("recommended_hotels", [])
    if hotels:
        lines.append("=" * 50)
        lines.append("RECOMMENDED HOTELS")
        lines.append("=" * 50)
        for i, hotel in enumerate(hotels, 1):
            lines.append(f"  {i}. {hotel.get('name', '?')}")
            summary = hotel.get("summary", "")
            if summary:
                lines.append(f"     Summary: {summary}")
            hotel_class = hotel.get("hotel_class")
            rating = hotel.get("rating")
            reviews = hotel.get("reviews")
            price = hotel.get("price_per_night")
            total = hotel.get("total_price")
            if hotel_class:
                lines.append(f"     Star rate: {hotel_class}")
            if rating:
                rating_text = f"{rating}/5"
                if reviews:
                    rating_text += f" from {reviews} reviews"
                lines.append(f"     Rating: {rating_text}")
            if price:
                lines.append(f"     Price: {price} per night")
            if total:
                lines.append(f"     Total: {total}")
            address = hotel.get("address")
            location_rating = hotel.get("location_rating")
            if address:
                lines.append(f"     Address: {address}")
            if location_rating:
                lines.append(f"     Location rating: {location_rating}/5")
            lines.append(f"     Quality: {hotel.get('quality_reason', '')}")
            lines.append(f"     Location: {hotel.get('proximity_reason', '')}")
            nearby_summary = hotel.get("nearby_summary", [])
            if nearby_summary:
                lines.append(f"     Nearby: {'; '.join(nearby_summary)}")
            services = hotel.get("services", [])
            if services:
                lines.append(f"     Services: {', '.join(services)}")
            review_summary = hotel.get("review_summary", [])
            if review_summary:
                lines.append(f"     Review notes: {'; '.join(review_summary)}")
            property_link = hotel.get("property_link")
            if property_link:
                lines.append(f"     Details: {property_link}")
            lines.append("")

    model_info = results.get("model_info", {})
    if model_info:
        lines.append("=" * 50)
        lines.append("MODEL USED")
        lines.append("=" * 50)
        lines.append(f"  Provider: {model_info.get('provider', '?')}")
        lines.append(f"  Backend: {model_info.get('backend', '?')}")
        lines.append(f"  Model: {model_info.get('model', '?')}")
        api_base = model_info.get("api_base")
        if api_base:
            lines.append(f"  API base: {api_base}")
        timeout = model_info.get("timeout_seconds")
        if timeout:
            lines.append(f"  Timeout: {timeout}s")
        lines.append("")

    return "\n".join(lines)


def save_text(filename: str, text: str) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(text)


def save_json(filename: str, data: dict) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
