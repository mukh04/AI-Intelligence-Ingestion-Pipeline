import pandas as pd
from pathlib import Path
from ..config import DATA_DIR

def export_all(startups, products, papers, jobs, news, mappings):
    datasets = {
        "startups.csv": startups,
        "products.csv": products,
        "research_papers.csv": papers,
        "jobs.csv": jobs,
        "news.csv": news,
        "entity_mapping_log.csv": mappings,
    }
    for filename, rows in datasets.items():
        pd.DataFrame(rows).to_csv(DATA_DIR / filename, index=False, encoding="utf-8-sig")
    return {name:len(rows) for name, rows in datasets.items()}
