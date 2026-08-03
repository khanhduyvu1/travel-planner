# QWEN.md — Project Tracking

## Codebase Analysis (2026-08-03)

### Project Overview
**AI Travel Planner** — A full-stack web app that combines real flight/hotel/restaurant data with AI-generated travel recommendations.

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, LiteLLM, SerpAPI |
| Frontend | React 19, Vite 8, Tailwind CSS 4 |
| AI Models | Provider-agnostic via LiteLLM (default: Qwen via DashScope) |
| External APIs | SerpAPI (Google Flights, Google Hotels, Google Maps) |

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (React + Vite + Tailwind)                      │
│  SearchForm → LoadingScreen → Results                    │
│  API service layer → POST /api/recommendations           │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (localhost:8000)
┌──────────────────────▼──────────────────────────────────┐
│  Backend (FastAPI)                                       │
│                                                          │
│  api/routes.py        — 2 endpoints: /flights, /recs     │
│  api/schemas.py       — Pydantic request/response models │
│                                                          │
│  planner/service.py   — Core orchestration logic         │
│  planner/prompts.py   — LLM system/user prompt templates │
│  planner/output.py    — Text/JSON rendering + file I/O   │
│                                                          │
│  flights/search.py    — SerpAPI Google Flights           │
│  hotels/search.py     — SerpAPI Google Hotels            │
│  restaurants/search.py— SerpAPI Google Maps restaurants  │
│  weather/search.py    — Open-Meteo geocoding + forecast  │
│                                                          │
│  rag/memory.py        — JSON-backed destination memory   │
│  AI_model.py          — Provider-agnostic LLM client     │
│  config.py            — Env-based LLM configuration      │
│  main.py              — CLI entry point                  │
│  server.py            — FastAPI app entry point           │
└──────────────────────────────────────────────────────────┘
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `backend/config.py` | Reads env vars for LLM provider, model, API base, timeout |
| `backend/AI_model.py` | `LLMClient` class wrapping LiteLLM; `get_client()` factory |
| `backend/planner/service.py` | Airport resolution, recommendation pipeline, hotel ranking, `expand_locations_to_days()` |
| `backend/planner/prompts.py` | System + user prompt templates for flights/places and hotels |
| `backend/planner/output.py` | `render_text()`, `save_text()`, `save_json()` for output files |
| `backend/flights/search.py` | SerpAPI Google Flights search, extraction, formatting |
| `backend/hotels/search.py` | SerpAPI Google Hotels search, extraction, formatting |
| `backend/restaurants/search.py` | SerpAPI Google Maps restaurant search per location |
| `backend/weather/search.py` | Open-Meteo geocoding + daily forecast + weather distribution |
| `backend/rag/memory.py` | `learn_from_locations()` + `retrieve_context()` for destination memory |
| `backend/api/routes.py` | FastAPI routes: `/api/flights`, `/api/recommendations` |
| `backend/api/schemas.py` | Pydantic models for all request/response types |

### Frontend Components

| Component | Purpose |
|-----------|---------|
| `App.jsx` | Root component with view state machine (search → loading → results) |
| `SearchForm.jsx` | Trip input form (cities, dates, budget, stops) |
| `LoadingScreen.jsx` | Animated loading spinner |
| `Results.jsx` | Displays flights, locations, hotels, itinerary with restaurant data |
| `services/api.js` | Fetch wrapper for `/api/flights` and `/api/recommendations` |

### Data Flow (Recommendation Pipeline)
1. User submits form → frontend POSTs to `/api/recommendations`
2. Backend resolves city → IATA airport codes via LLM
3. SerpAPI fetches real flights (Google Flights engine)
4. RAG retrieves learned destination context from `knowledge_cache/`
5. LLM generates 8 location recommendations + top 3 flights (JSON)
6. `learn_from_locations()` saves locations to destination memory
7. SerpAPI fetches real hotels (Google Hotels engine)
8. LLM ranks 3–5 best hotels based on proximity to recommended places
9. For each location, SerpAPI fetches nearby restaurants (Google Maps)
10. Top 2 restaurants assigned per location (lunch + dinner)
11. Locations expanded to day-by-day itinerary via `expand_locations_to_days()`
12. ~~Open-Meteo weather~~ — **disabled** (kept for future bot chat use)
13. Results rendered as text + JSON, saved to `backend/output/`

### RAG / Destination Memory System
- JSON files stored in `backend/knowledge_cache/` (one per destination)
- Tracks: times recommended, common reasons, things to do, suggested days history
- Confidence scoring based on recommendation frequency and data richness
- Text deduplication with similarity matching (72% word overlap threshold)
- Injected into LLM prompt as "Learned destination context"

### Configuration
- Default LLM: `qwen-plus` via DashScope (`https://dashscope.aliyuncs.com/compatible-mode/v1`)
- Supports switching to any LiteLLM provider via env vars
- SerpAPI key optional (skips flight/hotel/restaurant search if absent)
- CORS allows `localhost:5173` (Vite dev) and `localhost:3000`

### Output Files (in `backend/output/`)
- `recommendations.txt` / `.json` — Full travel plan
- `flights.txt` / `.json` — Raw + formatted flight data
- `hotels.txt` / `.json` — Raw + formatted hotel data
- `rag_context.txt` — Retrieved destination memory

### Notable Design Patterns
- **Provider-agnostic LLM**: `LLMClient` abstracts over OpenAI/Anthropic/Gemini/etc via LiteLLM
- **Retry on empty response**: Auto-retries with higher `max_tokens` if LLM returns empty
- **Temperature skip**: Omits temperature param for Gemini (unsupported)
- **Graceful degradation**: Each SerpAPI call wrapped in try/except; pipeline continues on failure
- **JSON extraction fallback**: Parses JSON from LLM output even with markdown wrapping
- **Module-level caching**: `_airport_cache` dict avoids redundant LLM calls for airport codes

### Current State
- ✅ CLI mode (`python -m backend.main`)
- ✅ API mode (`python -m backend.server` → FastAPI on port 8000)
- ✅ Frontend dev server (`npm run dev` → Vite on port 5173)
- ✅ Flight search + AI recommendation
- ✅ Hotel search + AI ranking
- ✅ Restaurant enrichment per location
- ✅ Day-by-day itinerary (multi-day locations split into separate days)
- ✅ RAG destination memory with confidence scoring
- ✅ Full React UI with Tailwind styling
- ⏸️ Weather integration — code exists in `backend/weather/`, disabled in pipeline (Open-Meteo 16-day limit)

---

## Change Log

| Date | Action |
|------|--------|
| 2026-08-03 | Initial codebase analysis — no changes made |
| 2026-08-03 | Added weather API integration (Open-Meteo, no API key needed) |
| 2026-08-03 | Fixed itinerary: each day = 1 location, multi-day locations split, weather 1:1 per day |
| 2026-08-03 | Fixed weather 400 error: Open-Meteo only supports 16-day forecast from today, added cap |
| 2026-08-03 | Disabled weather in pipeline (kept `backend/weather/` module for future bot chat use) |

### Weather Feature Details (2026-08-03)

**New files:**
- `backend/weather/search.py` — Open-Meteo geocoding + daily forecast fetch + `distribute_weather()` helper
- `backend/weather/__init__.py` — Module exports

**Modified files:**
- `backend/api/schemas.py` — Added `DayWeather` model; added `weather: list[DayWeather]` to `Location`
- `backend/api/routes.py` — Imports weather module; fetches + distributes weather after restaurant enrichment
- `backend/main.py` — Same weather integration for CLI pipeline
- `backend/planner/output.py` — Renders weather per location in text output
- `frontend/src/components/Results.jsx` — Weather forecast section in `ItineraryCard` (icon, description, temp range, precipitation %)

**How it works:**
1. After locations are generated, `fetch_weather()` geocodes the destination via Open-Meteo
2. Fetches daily forecast (temp max/min, precipitation probability, WMO weather code) for trip date range
3. `distribute_weather()` maps forecast days → locations based on each location's `suggested_days`
4. Weather is wrapped in try/except — pipeline continues gracefully if weather API fails
5. Frontend shows weather cards in each itinerary day with emoji icon, description, temperature range, and rain probability

### Itinerary Fix Details (2026-08-03)

**Problem:** Locations with `suggested_days > 1` caused weather mismatch — some days had weather, some didn't.

**Solution:** Added `expand_locations_to_days()` in `backend/planner/service.py` that splits multi-day locations into separate single-day entries before weather distribution.

**Example:**
- Before: `[{name: "Old Quarter", suggested_days: 2}, ...]` → 5 locations, weather mismatch
- After: `[{name: "Old Quarter", day_label: "Day 1 of 2"}, {name: "Old Quarter", day_label: "Day 2 of 2"}, ...]` → 7 days, each with 1 weather

**Modified files:**
- `backend/planner/service.py` — Added `expand_locations_to_days()` function
- `backend/planner/__init__.py` — Exported new function
- `backend/api/routes.py` — Calls expand before weather distribution
- `backend/main.py` — Same for CLI pipeline
- `backend/api/schemas.py` — Added `day_label: str` field to `Location`
- `frontend/src/components/Results.jsx` — ItineraryCard shows "Day N" header; "Places to Visit" deduplicates by name
