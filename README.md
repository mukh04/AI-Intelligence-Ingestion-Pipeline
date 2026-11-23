# AI Intelligence Ingestion Pipeline

Async Python pipeline for collecting AI ecosystem signals, enriching research papers with GitHub metrics, applying optional LLM extraction, resolving entity-name variants, and exporting six CSV datasets.

## Quick start (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
# Add your own Gemini key to .env if using LLM enrichment
python -m src.main
```

## Outputs

The pipeline writes `startups.csv`, `products.csv`, `research_papers.csv`, `jobs.csv`, `news.csv`, and `entity_mapping_log.csv` under `data/`.

## What is implemented

- Async HTTP collection with bounded concurrency, timeouts, retries and jittered backoff.
- arXiv Atom API paper collection (up to configured `MAX_ARXIV_RESULTS`).
- GitHub REST enrichment for repository links detected in paper metadata.
- RSS/Atom ingestion for configured news and job feeds, with strict rolling 24-hour date filtering; entries without a parseable date are excluded.
- RapidFuzz-assisted canonical entity matching.
- Optional Gemini JSON extraction with bounded chunking and safe JSON parsing.
- CSV export for the six requested datasets.

## Known gaps — do not misrepresent these

The supplied snapshot is a working foundation, not a fully compliant final dataset. Its current CSV snapshot contains 2 startup seed examples, 1 product seed example, 1,000 research papers, 220 job feed entries, 9 news feed entries, and 3 entity mapping log rows. The startup/product rows are explicitly marked as seed examples, not scraped records. The counts in the files are snapshot counts, not a guarantee of current freshness.

The configured news and job source lists each contain five feed URLs, but the supplied snapshot only demonstrates records from a subset of those sources. Verify successful collection from all ten sources in a fresh run. Re-check the strict 24-hour window at submission time.

Gemini is the only implemented LLM provider in this snapshot. Groq and DeepSeek are not implemented as working fallback adapters. Do not claim the required Gemini → Groq → DeepSeek chain is complete until provider adapters, error handling, and tests are implemented.

Startup and product directory URL constants are not functional collectors. Do not count seed examples toward the 1,000-record requirements. Add permitted official API/directory adapters and validate every record's source URL before claiming compliance.

## Data integrity

Never fabricate records or ask an LLM to invent facts. Keep missing values null. Retain the original source URL and collection timestamp. Respect source terms, robots.txt, rate limits, and access controls; do not bypass CAPTCHAs or authentication barriers.

## Scaling design

For 500k+ records, this single-process CSV implementation should be evolved into a distributed architecture: scheduler → durable queue → stateless async workers → validation/deduplication → PostgreSQL/object storage → search/graph index → export/API. Add idempotency keys, dead-letter queues, observability, checkpointing, and backpressure. See `architecture.pdf`.

## Environment variables

See `.env.example`. Keep `.env` local and never commit credentials. The `.gitignore` excludes `.env`, virtual environments, bytecode, and logs while allowing the required CSV deliverables to be committed.
