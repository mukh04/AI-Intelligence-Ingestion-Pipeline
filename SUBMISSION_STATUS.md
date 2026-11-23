# Submission status — verified snapshot

This package is cleaned and documented, but it is **not yet fully compliant** with the assignment's minimum data/source requirements.

Snapshot counts checked from the supplied CSV files:

| Dataset | Rows | Assessment requirement / note |
|---|---:|---|
| Startups | 2 | Below 1,000; both rows are seed examples, not scraped records |
| Products | 1 | Below 1,000; seed example, not a scraped record |
| Research papers | 1,000 | Meets row-count target; verify source URLs and GitHub metrics |
| Jobs | 220 | Must be rechecked for rolling 24-hour freshness and five distinct active sources |
| News | 9 | Must be rechecked for rolling 24-hour freshness and five distinct active sources |
| Entity mapping log | 3 | Small demonstration log |

## Known implementation gaps
- Startup/product directory URL constants exist, but collectors are not implemented.
- The supplied snapshot does not demonstrate successful records from all five news and five job sources.
- Gemini is implemented; Groq and DeepSeek fallback adapters are placeholders.
- The architecture PDF describes both current implementation and proposed 500k+ production architecture, clearly distinguishing them.

## Before submission
1. Re-run the pipeline and verify the jobs/news dates against the exact submission time.
2. Add permitted startup/product source adapters and collect genuine records with source URLs.
3. Implement and test Groq and DeepSeek fallback adapters if claiming the full chain.
4. Verify every row's provenance and remove invalid/duplicate records.
5. Keep `.env` local; commit `.env.example` only.
