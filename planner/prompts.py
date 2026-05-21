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
1. If flight data is provided above, pick the top 3 best flights and explain briefly why each is a good choice
   (e.g. cheapest, fastest, best airline, fewest stops).
   The budget above is only for in-city activities and does NOT apply to flights.
   Include the flight number from the list (1, 2, 3, ...) as "flight_index".
   Copy the exact summary from the flight list -- do NOT make up or modify airline names, routes, durations, or prices.
   If NO flight data is provided above, set recommended_flights to an EMPTY list []. NEVER invent flights.

2. Recommend exactly 8 specific locations/areas within {destination} that the traveler should visit.
  Prioritize well-known landmarks, museums, neighborhoods, parks, temples, markets, waterfronts, or historic sites.
  For each location, provide "details" with 2-4 specific sentences about what the place is like, its cultural or historical context, and what kind of traveler would enjoy it.
  Also explain why it's worth visiting and what to do there.

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
      "details": "2-4 specific sentences with context, atmosphere, history, or practical notes about this location",
      "why": "why this place is worth visiting",
      "things_to_do": ["activity 1", "activity 2", "activity 3"],
      "suggested_days": 1
    }}
  ],
  "total_estimated_budget": 0
}}

The "locations" array must contain exactly 8 objects.
""".strip()
