import json, logging, asyncio, random
from ..config import GEMINI_API_KEY, GEMINI_MODEL
from .chunking import semantic_chunks

log = logging.getLogger(__name__)

class LLMOrchestrator:
    def __init__(self):
        self.gemini = None
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as exc:
                log.warning("Gemini client unavailable: %s", exc)

    async def extract_json(self, text, schema_description="Extract factual fields only"):
        """Gemini is optional enrichment. Never use it to manufacture source facts."""
        if not self.gemini:
            return {"status":"skipped", "reason":"Gemini API key/client unavailable", "chunks":len(semantic_chunks(text))}
        chunks = semantic_chunks(text)
        results = []
        for chunk in chunks:
            prompt = (
                "Return valid JSON only. Extract only facts explicitly present in the source text. "
                "Use null for missing fields. Do not infer or invent URLs, dates, counts, companies, or metrics.\n"
                f"Task: {schema_description}\nSource text:\n{chunk}"
            )
            for attempt in range(4):
                try:
                    response = await asyncio.to_thread(
                        self.gemini.models.generate_content,
                        model=GEMINI_MODEL, contents=prompt
                    )
                    raw = (response.text or "").strip()
                    raw = raw.removeprefix("```json").removesuffix("```").strip()
                    results.append(json.loads(raw))
                    break
                except Exception as exc:
                    msg = str(exc)
                    # Retry rate limits/transient errors with exponential backoff + jitter.
                    if attempt < 3 and any(x in msg.lower() for x in ("429","503","rate","temporar","timeout")):
                        await asyncio.sleep(min(2**attempt + random.random(), 20))
                        continue
                    log.warning("Gemini extraction failed: %s", exc)
                    results.append({"error":"extraction_failed"})
                    break
        return {"status":"ok", "results":results, "chunks":len(chunks)}
