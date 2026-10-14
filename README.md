# EquityScope
A stock research workspace by Elliott Kim. React + FastAPI + PostgreSQL, with Alpha Vantage market-data integration and evidence-linked AI briefs.

## What works
- Six-stock demo with explicitly synthetic daily prices, illustrative metrics, and fictional news.
- Interactive charts, date ranges, 20-day SMA, Wilder RSI, stock search, sentiment filters, comparison table, browser-persisted watchlist.
- FastAPI endpoints for provider daily history, company fundamentals, ticker news sentiment, and optional OpenAI research summaries.
- PostgreSQL-backed stock snapshot cache (30 minutes), provider error handling, evidence ID validation, configurable CORS.

## Quick start
Requires Node 20+, Python 3.11+, and Docker for PostgreSQL.

```bash
docker compose up -d
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env, then:
uvicorn main:app --reload --env-file .env
```

In another terminal:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. The app starts in demo mode. Expand **Connect your local backend**, leave the backend URL empty to use Vite's proxy, and click **Load provider data**. You can also use http://localhost:8000 explicitly. The API docs are at http://localhost:8000/docs.

For SQLite without Docker, replace DATABASE_URL with sqlite:///./research.db. The local sample app works without any API keys.

## API
- GET /api/health — configuration flags
- GET /api/stocks/{symbol} — daily prices, indicators, fundamentals, news; database cached
- POST /api/stocks/{symbol}/analysis — evidence-linked AI brief; requires an OpenAI key

## Data and AI
Alpha Vantage integration uses TIME_SERIES_DAILY, OVERVIEW and NEWS_SENTIMENT. Provider entitlements and quotas vary; a new ticker requires three sequential requests. Compact daily history may offer fewer than 252 sessions; range selectors display available data. Daily closes are unadjusted, so splits and dividends can distort indicators. Reporting periods for fundamentals and prices differ. The UI does not use real-time quotes.

News sentiment in live mode comes from the provider's NLP scores; this project does not train its own classifier. Summaries are generated server-side with the OpenAI Responses API, only when OPENAI_API_KEY is configured. Demo briefs are deterministic editorial samples, not model output. Summary factors reference news IDs shown on article cards; uncited metric factors are permitted. The prompt prohibits causal claims and instructions from article text. Output structure and source IDs are validated, but that does not prove every generated claim is accurate.

## Deployment
`npm run build` in frontend produces dist/. The published private preview contains the React frontend and demo data; it does not host Python or PostgreSQL. Deploy FastAPI separately and set VITE_API_URL at frontend build time plus an appropriate CORS_ORIGINS on the backend to connect them. Keep keys server-side. This is a personal development project; add authentication and API rate limiting before exposing the backend publicly. Watchlists are browser-local, not database-backed.

## Verification
```bash
cd backend
PYTHONPATH=. python -m pytest tests
cd ../frontend
npm run build
```
Six backend tests cover indicator warm-up windows, RSI reference/edge cases, missing credentials, symbol validation, database caching, unsafe URL removal, and rejection of invented AI source references. The React production build and six-stock demo-data checks also passed. Browser UI verification was unavailable. Live provider and AI calls require keys and were not exercised in the delivered environment.

## Next extensions
Train/evaluate a financial-news classifier against labeled data, add earnings-event overlays, synchronize authenticated watchlists, or add a job queue for ingestion. Keep observed price movements separate from hypotheses about their causes.

## References
- https://www.alphavantage.co/documentation/
- https://developers.openai.com/api/reference/resources/responses/
