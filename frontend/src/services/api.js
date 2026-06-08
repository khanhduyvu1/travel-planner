const API_BASE = "http://127.0.0.1:8000/api";

export async function searchFlights({ departureCode, arrivalCode, startDate, returnDate, maxStops }) {
  const res = await fetch(`${API_BASE}/flights`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      departure_code: departureCode,
      arrival_code: arrivalCode,
      start_date: startDate,
      return_date: returnDate || null,
      max_stops: maxStops ?? null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Flight search failed (${res.status})`);
  }

  return res.json();
}

export async function getRecommendations({
  startCity,
  destination,
  startDate,
  returnDate,
  estimatedBudget,
  maxStops,
}) {
  const res = await fetch(`${API_BASE}/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      start_city: startCity,
      destination: destination,
      start_date: startDate,
      return_date: returnDate || null,
      estimated_budget: estimatedBudget?.trim() || null,
      max_stops: maxStops ?? null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Recommendation failed (${res.status})`);
  }

  return res.json();
}
