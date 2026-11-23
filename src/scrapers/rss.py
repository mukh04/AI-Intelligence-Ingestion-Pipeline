import feedparser, asyncio, logging
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from ..sources import NEWS_FEEDS, JOB_FEEDS
from ..http_client import AsyncHTTP

log = logging.getLogger(__name__)

def parse_entry_date(entry):
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if value:
            try:
                dt = parsedate_to_datetime(value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            try:
                import time
                return datetime.fromtimestamp(time.mktime(value), tz=timezone.utc)
            except Exception:
                pass
    return None

async def collect_feeds(http: AsyncHTTP, feeds, record_type):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    output = []
    async def one(source, url):
        text = await http.get_text(url)
        if not text:
            return []
        parsed = feedparser.parse(text)
        rows = []
        for entry in parsed.entries:
            dt = parse_entry_date(entry)
            # Strict policy: exclude records with missing/ambiguous dates.
            if dt is None or dt < cutoff:
                continue
            link = entry.get("link")
            title = entry.get("title", "").strip()
            if not link or not title:
                continue
            rows.append({
                "schemaVersion":"1.0", "recordType":record_type,
                "title":title, "company":None, "url":link,
                "date":dt.isoformat(), "is_remote":None,
                "role_family":None, "content":entry.get("summary",""),
                "source_name":source, "source_url":link
            })
        return rows
    batches = await asyncio.gather(*(one(k,v) for k,v in feeds.items()))
    for batch in batches:
        output.extend(batch)
    return output

async def collect_news(http):
    return await collect_feeds(http, NEWS_FEEDS, "NEWS")

async def collect_jobs(http):
    return await collect_feeds(http, JOB_FEEDS, "JOB")
