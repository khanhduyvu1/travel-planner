# AI Travel Planner

A CLI and web app that combines real flight data with AI-generated travel recommendations.

## How It Works

1. You enter your departure city, destination, travel dates, budget, and stop preferences.
2. The app resolves city names to IATA airport codes using the configured AI model.
3. Real flights are fetched from Google Flights via SerpAPI when `SERPAPI_KEY` is configured.
4. The configured AI model analyzes the flights and destination to produce:
   - Top 3 recommended flights with reasoning
   - 5 places to visit with activities and suggested duration
5. Results are saved as both human-readable text and structured JSON.

## Prerequisites

- Python 3.12+
- An AI provider supported by [LiteLLM](https://docs.litellm.ai/), such as Ollama, OpenAI, Anthropic, Gemini, or Groq
- For local models: [Ollama](https://ollama.com/) installed and running locally
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
pip install -r requirements.txt

# Optional, for local Ollama usage
ollama pull llama3
```

Create a `.env` file in the project root:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3
LLM_API_BASE=http://127.0.0.1:11434
LLM_TIMEOUT=300
SERPAPI_KEY=your_serpapi_key_here
```

`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_BASE`, and `LLM_TIMEOUT` are optional if you use the local Ollama defaults above. `SERPAPI_KEY` is optional. Without it, the app skips flight search and only generates destination recommendations.

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

You can also set `LLM_MODEL` to a full LiteLLM model name, such as `ollama/qwen2.5`, `openai/gpt-4o-mini`, or `anthropic/claude-3-5-sonnet-latest`.

## Usage

Run the CLI:

```bash
python main.py
```

Run the API:

```bash
python server.py
```

Run the frontend from `frontend/`:

```bash
npm run dev
```

## Output

The app writes generated files to `output/`:

| File | Description |
|---|---|
| `recommendations.txt` | Human-readable travel plan |
| `recommendations.json` | Structured JSON of recommendations |
| `flights.txt` | Formatted flight options summary |
| `flights.json` | Raw flight data from SerpAPI |

## Project Structure

```text
main.py              # CLI entry point
AI_model.py          # Provider-agnostic AI client setup
server.py            # FastAPI app entry point
api/                 # API routes and schemas
planner/             # Airport resolution, prompts, recommendations, output saving
flights/             # SerpAPI Google Flights integration
frontend/            # React/Vite web UI
requirements.txt
```

## APIs Used

- **LiteLLM** -- model routing for Ollama, OpenAI, Anthropic, Gemini, Groq, and other providers
- **SerpAPI** -- Google Flights engine for real-time flight search
