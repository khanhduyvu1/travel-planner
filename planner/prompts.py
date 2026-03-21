SYSTEM_PROMPT = """
You are an expert travel planner. Given a destination, dates, budget, and available flights,
you recommend the best flights and the best places to visit within the destination city.
You MUST output only valid JSON (UTF-8). No markdown, no extra text.
If you cannot comply, output {{"error":"invalid_output"}}.
""".strip()

USER_PROMPT_TEMPLATE = """
Destination: {destination}
Trip start date: {start_date}
Return date: {return_date}
Budget for activities in the city (excludes flights): {estimated_budget}

{flight_section}

Task:
1. From the numbered flight list above, you MUST pick the top 3 best flights and explain briefly why each is a good choice
   (e.g. cheapest, fastest, best airline, fewest stops).
   The budget above is only for in-city activities and does NOT apply to flights.
   Include the flight number from the list (1, 2, 3, ...) as "flight_index".
   Only set recommended_flights to an empty list if there is NO flight data at all.

2. Recommend 5 specific locations/areas within {destination} that the traveler should visit.
   For each location explain why it's worth visiting and what to do there.

Return JSON with this exact shape:
{{
  "destination": "{destination}",
  "recommended_flights": [
    {{
      "flight_index": 1,
      "summary": "one-line flight summary (airline, route, duration, price)",
      "reason": "why this flight is recommended"
    }}
  ],
  "locations": [
    {{
      "name": "specific place or area name",
      "why": "why this place is worth visiting",
      "things_to_do": ["activity 1", "activity 2", "activity 3"],
      "suggested_days": 1
    }}
  ],
  "total_estimated_budget": 0
}}
""".strip()
