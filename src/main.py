import asyncio, logging
from datetime import datetime, timezone
from .config import LOG_DIR
from .http_client import AsyncHTTP
from .scrapers.arxiv import collect_arxiv, enrich_github
from .scrapers.rss import collect_news, collect_jobs
from .processing.entity_resolver import mapping_log
from .storage.exporter import export_all
from .llm.llm_orchestrator import LLMOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"), logging.StreamHandler()]
)
log = logging.getLogger("pipeline")

# These are canonical seed entities for testing resolver/export wiring only.
# They are deliberately not counted as acquired records; replace with source adapters.
SEED_STARTUPS = [
    {"schemaVersion":"1.0","recordType":"STARTUP","source_name":"Official company website","source_url":"https://openai.com/","entityName":"OpenAI","employeeCount":None,"collectedAt":datetime.now(timezone.utc).isoformat(),"record_status":"seed_example_not_scraped"},
    {"schemaVersion":"1.0","recordType":"STARTUP","source_name":"Official company website","source_url":"https://www.anthropic.com/","entityName":"Anthropic","employeeCount":None,"collectedAt":datetime.now(timezone.utc).isoformat(),"record_status":"seed_example_not_scraped"},
]
SEED_PRODUCTS = [
    {"schemaVersion":"1.0","recordType":"PRODUCT","source_name":"Official product website","source_url":"https://chatgpt.com/","startupName":"OpenAI","entityName":"ChatGPT","pricingModel":None,"collectedAt":datetime.now(timezone.utc).isoformat(),"record_status":"seed_example_not_scraped"},
]

async def run():
    log.info("Starting AI Intelligence Ingestion Pipeline")
    async with AsyncHTTP() as http:
        papers = await collect_arxiv(http)
        papers = await enrich_github(http, papers)
        news = await collect_news(http)
        jobs = await collect_jobs(http)

    # Seed examples are explicitly marked and must not be represented as scraped counts.
    startups, products = SEED_STARTUPS, SEED_PRODUCTS
    names = [x.get("entityName") for x in startups] + [x.get("entityName") for x in products]
    mappings = mapping_log(names)

    llm = LLMOrchestrator()
    llm_status = await llm.extract_json(
        "Pipeline run. Do not create records. Return {\"pipeline\":\"AI Intelligence Ingestion Pipeline\"}.",
        "Return a one-field pipeline status JSON object."
    )

    counts = export_all(startups, products, papers, jobs, news, mappings)
    log.info("Export counts: %s", counts)
    log.info("LLM status: %s", llm_status.get("status"))
    print("\nPIPELINE FINISHED")
    for name, count in counts.items():
        print(f"{name}: {count}")
    print("\nNote: startup/product rows are clearly labelled seed examples, not scraped records.")
    print("Research paper counts and fresh signal counts above are the actual records collected.")

if __name__ == "__main__":
    asyncio.run(run())
