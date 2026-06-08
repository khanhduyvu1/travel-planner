# AI Travel Planner

A CLI and web app that combines real flight data with AI-generated travel recommendations.

## How It Works

1. You enter your departure city, destination, travel dates, optional budget, and stop preferences.
2. The app resolves city names to IATA airport codes using the configured AI model.
3. Real flights are fetched from Google Flights via SerpAPI when `SERPAPI_KEY` is configured.
4. The configured AI model analyzes the flights and destination to produce:
   - Top 3 recommended flights with reasoning
   - 3-5 recommended hotels with price, star rate, rating, services, Google Maps details, and location reasoning
   - 8 places to visit with activities and suggested duration
5. Results are saved as both human-readable text and structured JSON.

The app also keeps a lightweight destination memory in `backend/knowledge_cache/`.
After each successful trip plan, it learns which locations were recommended and reuses that context
to improve future place recommendations for the same destination.

## Prerequisites

- Python 3.12+
- An open AI provider, such as GitHub Models or a provider supported by [LiteLLM](https://docs.litellm.ai/) like OpenAI, Anthropic, Gemini, or Groq
- Optional: a [SerpAPI key](https://serpapi.com/) for real flight data

## Setup

```bash
# Clone the repo
git clone https://github.com/your-username/ai-travel-planner.git
cd ai-travel-planner

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r backend/requirements.txt
```

Create a `.env` file in the project root:

```env
LLM_PROVIDER=github
LLM_MODEL=openai/gpt-4o-mini
GITHUB_TOKEN=your_github_token_here
LLM_TIMEOUT=300
LLM_MAX_RETRIES=2
SERPAPI_KEY=your_serpapi_key_here
```

`LLM_PROVIDER`, `LLM_MODEL`, `LLM_TIMEOUT`, and `LLM_MAX_RETRIES` are optional if you use the defaults above. `SERPAPI_KEY` is optional. Without it, the app skips flight search and only generates destination recommendations.

To switch providers, change only your `.env` values:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_key_here
```

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-latest
ANTHROPIC_API_KEY=your_anthropic_key_here
```

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini/gemini-1.5-flash
GEMINI_API_KEY=your_gemini_key_here
```

You can also set `LLM_MODEL` to a full LiteLLM model name, such as `openai/gpt-4o-mini`, `anthropic/claude-3-5-sonnet-latest`, or `gemini/gemini-1.5-flash`.

The activity budget field is optional. If you leave it blank, the app asks the model for recommendations without a budget limit.

## Usage

Run the CLI:

```bash
python -m backend.main
```

Run the API:

```bash
python -m backend.server
```

Or from inside `backend/`:

```bash
python server.py
```

Run the frontend from `frontend/`:

```bash
npm run dev
```

## Output

The app writes generated files to `backend/output/`:

| File | Description |
|---|---|
| `recommendations.txt` | Human-readable travel plan |
| `recommendations.json` | Structured JSON of recommendations |
| `flights.txt` | Formatted flight options summary |
| `flights.json` | Raw flight data from SerpAPI |
| `hotels.txt` | Formatted hotel options summary |
| `hotels.json` | Structured hotel data from SerpAPI |
| `rag_context.txt` | Learned destination memory injected into the recommendation prompt |

Learned destination memory is written to `backend/knowledge_cache/` as JSON files.
Repeated locations are ranked with a confidence score so future searches use cleaner, stronger memory.

## Project Structure

```text
backend/
  main.py            # CLI entry point
  AI_model.py        # Provider-agnostic AI client setup
  server.py          # FastAPI app entry point
  api/               # API routes and schemas
  planner/           # Airport resolution, prompts, recommendations, output saving
  flights/           # SerpAPI Google Flights integration
  hotels/            # SerpAPI Google Hotels integration
  rag/               # JSON-backed destination memory retrieval
  knowledge_cache/   # Learned destination location memory
  requirements.txt
frontend/            # React/Vite web UI
```

## APIs Used

- **LiteLLM** -- model routing for OpenAI, Anthropic, Gemini, Groq, and other open providers
- **SerpAPI** -- Google Flights and Google Hotels engines for real-time travel search
