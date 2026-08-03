from datetime import datetime, timedelta

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WMO_DESCRIPTION = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Light freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "🌧️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


def _geocode(destination: str) -> tuple[float, float] | None:
    resp = requests.get(
        GEOCODING_URL,
        params={"name": destination, "count": 1, "language": "en"},
        timeout=15,
    )
    resp.raise_for_status()
    results = resp.json().get("results") or []
    if not results:
        return None
    return results[0]["latitude"], results[0]["longitude"]


def _weather_description(code: int) -> tuple[str, str]:
    return WMO_DESCRIPTION.get(code, ("Unknown", "🌡️"))


def _total_trip_days(locations: list[dict], fallback: int = 7) -> int:
    """Sum suggested_days across locations to know how many weather days we need."""
    total = 0
    for loc in locations:
        if not isinstance(loc, dict):
            continue
        d = loc.get("suggested_days", 1)
        total += int(d) if isinstance(d, (int, float)) and d >= 1 else 1
    return max(total, 1) if total else fallback


def fetch_weather(
    destination: str,
    start_date: str,
    return_date: str | None = None,
    locations: list[dict] | None = None,
) -> list[dict]:
    """Fetch daily weather forecast for a destination. Returns a list of daily weather dicts."""
    coords = _geocode(destination)
    if not coords:
        return []

    lat, lon = coords

    if return_date:
        end = return_date
    else:
        num_days = _total_trip_days(locations) if locations else 7
        end = (
            datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=num_days - 1)
        ).strftime("%Y-%m-%d")

    # Open-Meteo forecast API only supports up to 16 days from today
    today = datetime.now().strftime("%Y-%m-%d")
    max_end = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
    if end > max_end:
        end = max_end
    if start_date > max_end:
        return []  # Trip is too far in the future for forecast

    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
            "start_date": start_date,
            "end_date": end,
            "timezone": "auto",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    daily = data.get("daily") or {}

    dates = daily.get("time") or []
    t_max = daily.get("temperature_2m_max") or []
    t_min = daily.get("temperature_2m_min") or []
    precip = daily.get("precipitation_probability_max") or []
    codes = daily.get("weathercode") or []

    unit = data.get("daily_units", {})
    temp_unit = unit.get("temperature_2m_max", "°C")

    days = []
    for i, date_str in enumerate(dates):
        code = codes[i] if i < len(codes) else 0
        description, icon = _weather_description(code)
        days.append({
            "date": date_str,
            "temp_max": round(t_max[i], 1) if i < len(t_max) else None,
            "temp_min": round(t_min[i], 1) if i < len(t_min) else None,
            "temp_unit": temp_unit,
            "precipitation_probability": precip[i] if i < len(precip) else None,
            "weather_code": code,
            "description": description,
            "icon": icon,
        })

    return days


def distribute_weather(
    locations: list[dict],
    weather_days: list[dict],
    start_date: str,
) -> None:
    """Assign weather forecast days to itinerary locations based on suggested_days."""
    if not weather_days or not locations:
        return

    day_index = 0
    for location in locations:
        if not isinstance(location, dict):
            continue
        if day_index >= len(weather_days):
            break

        num_days = location.get("suggested_days", 1)
        if isinstance(num_days, (int, float)) and num_days >= 1:
            count = int(num_days)
        else:
            count = 1

        assigned = []
        for _ in range(count):
            if day_index < len(weather_days):
                assigned.append(weather_days[day_index])
                day_index += 1
        location["weather"] = assigned
