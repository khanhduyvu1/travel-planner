import json
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

MODEL_NAME = "openai/gpt-4.1"


def collect_request() -> dict:
    stops_input = input("Max stops (0=nonstop, 1=1 stop, 2=2 stops, Enter=any): ").strip()
    max_stops = int(stops_input) if stops_input in ("0", "1", "2") else None

    return {
        "start_city": input("Where are you flying from? (city): ").strip(),
        "destination": input("Where are you going to? (city): ").strip(),
        "start_date": input("Start date (YYYY-MM-DD): ").strip(),
        "return_date": input("Return date (YYYY-MM-DD, Enter=one way): ").strip() or None,
        "estimated_budget": input("Estimated budget (e.g. 500 USD): ").strip(),
        "max_stops": max_stops,
    }


def resolve_airport_code(client, city: str) -> str:
    """Ask the LLM for the main IATA airport code of a city."""
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        max_tokens=10,
        messages=[
            {
                "role": "system",
                "content": "Reply with ONLY the 3-letter IATA airport code for the main international airport of the given city. No explanation, no punctuation, just the code.",
            },
            {"role": "user", "content": city},
        ],
    )
    return resp.choices[0].message.content.strip().upper()[:3]


def _parse_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise ValueError(f"Model did not return valid JSON:\n{text}")


def get_recommendations(
    client,
    *,
    destination: str,
    start_date: str,
    return_date: str,
    estimated_budget: str,
    flight_data: str = "",
) -> dict:
    flight_section = ""
    if flight_data:
        flight_section = f"Available flights:\n{flight_data}"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        destination=destination,
        start_date=start_date,
        return_date=return_date,
        estimated_budget=estimated_budget,
        flight_section=flight_section,
    )

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.7,
        top_p=1.0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = resp.choices[0].message.content
    return _parse_json(text)
