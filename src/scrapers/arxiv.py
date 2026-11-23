import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from ..config import MAX_ARXIV_RESULTS
from ..http_client import AsyncHTTP

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}

async def collect_arxiv(http: AsyncHTTP, max_results=None):
    limit = max_results or MAX_ARXIV_RESULTS
    papers, start, page_size = [], 0, 100
    while start < limit:
        params = {
            "search_query": '((cat:cs.AI) OR (cat:cs.LG) OR (cat:cs.CL) OR (cat:cs.CV))',
            "start": start, "max_results": min(page_size, limit-start),
            "sortBy": "submittedDate", "sortOrder": "descending"
        }
        xml_text = await http.get_text(ARXIV_API, params=params)
        if not xml_text:
            break
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            break
        entries = root.findall("a:entry", NS)
        if not entries:
            break
        for e in entries:
            title = " ".join((e.findtext("a:title", default="", namespaces=NS) or "").split())
            paper_url = (e.findtext("a:id", default="", namespaces=NS) or "").strip()
            published = (e.findtext("a:published", default="", namespaces=NS) or "").strip()
            authors = [x.findtext("a:name", default="", namespaces=NS) for x in e.findall("a:author", NS)]
            summary = " ".join((e.findtext("a:summary", default="", namespaces=NS) or "").split())
            if title and paper_url:
                papers.append({
                    "schemaVersion":"1.0", "recordType":"RESEARCH_PAPER",
                    "title":title, "authors":authors, "paper_url":paper_url,
                    "github_url":None, "github_stars":None,
                    "published_date":published, "abstract":summary,
                    "source_url":paper_url
                })
        start += len(entries)
        if len(entries) < page_size:
            break
    return papers

async def enrich_github(http: AsyncHTTP, papers):
    # Detect repository URLs in abstracts; do not ask the LLM to invent links.
    import re
    urls = {}
    for p in papers:
        matches = re.findall(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", p.get("abstract",""))
        if matches:
            urls[p["paper_url"]] = matches[0].rstrip(".,)")
    async def one(p):
        url = urls.get(p["paper_url"])
        if not url:
            return p
        parts = url.rstrip("/").split("/")
        if len(parts) < 2:
            return p
        api = f"https://api.github.com/repos/{parts[-2]}/{parts[-1]}"
        raw = await http.get_text(api)
        if raw:
            import json
            try:
                obj = json.loads(raw)
                p["github_url"] = obj.get("html_url", url)
                p["github_stars"] = obj.get("stargazers_count")
            except Exception:
                pass
        return p
    return await __import__("asyncio").gather(*(one(p) for p in papers))
