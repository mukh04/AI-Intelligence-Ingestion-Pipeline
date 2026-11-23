
import asyncio
import random
import logging
import os
import time
from urllib.parse import urlparse

import aiohttp
from dotenv import load_dotenv

from .config import REQUEST_CONCURRENCY, REQUEST_TIMEOUT

load_dotenv()

log = logging.getLogger(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()


class AsyncHTTP:
    def __init__(self):
        self.sem = asyncio.Semaphore(REQUEST_CONCURRENCY)
        self.github_sem = asyncio.Semaphore(1)

        self.timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.session = None

    async def __aenter__(self):
        headers = {
            "User-Agent": "AI-Intelligence-AssessmentBot/1.0",
            "Accept": "application/vnd.github+json",
        }

        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=headers
        )

        if GITHUB_TOKEN:
            log.info("GitHub token detected. Authenticated API requests enabled.")
        else:
            log.warning(
                "GITHUB_TOKEN not found. GitHub API requests will be unauthenticated."
            )

        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def get_text(self, url, params=None, attempts=3):

        is_github = urlparse(url).hostname == "api.github.com"

        request_headers = {}

        if is_github and GITHUB_TOKEN:
            request_headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

        async with self.sem:

            if is_github:
                async with self.github_sem:
                    return await self._request(
                        url, params, attempts, request_headers
                    )

            return await self._request(
                url, params, attempts, request_headers
            )

    async def _request(self, url, params, attempts, headers):

        for attempt in range(attempts):

            try:
                async with self.session.get(
                    url,
                    params=params,
                    headers=headers
                ) as response:

                    # Successful response
                    if response.status == 200:
                        return await response.text()

                    # GitHub rate limit
                    if response.status == 403 and urlparse(url).hostname == "api.github.com":

                        remaining = response.headers.get(
                            "X-RateLimit-Remaining"
                        )

                        reset = response.headers.get(
                            "X-RateLimit-Reset"
                        )

                        retry_after = response.headers.get("Retry-After")

                        if remaining == "0":
                            reset_time = int(reset) if reset else 0
                            wait = max(0, reset_time - int(time.time()))

                            log.error(
                                "GitHub API rate limit exhausted. "
                                "Reset in approximately %s seconds. "
                                "Skipping request: %s",
                                wait,
                                url
                            )

                            return None

                        # Secondary rate limit
                        if retry_after and attempt < attempts - 1:
                            wait = float(retry_after)

                            log.warning(
                                "GitHub secondary rate limit. "
                                "Waiting %.1f seconds.",
                                wait
                            )

                            await asyncio.sleep(wait)
                            continue

                        log.error(
                            "GitHub returned 403. Check token permissions "
                            "or secondary rate limits. URL: %s",
                            url
                        )

                        return None

                    # Temporary rate limits and server errors
                    if response.status in (429, 500, 502, 503, 504):

                        retry_after = response.headers.get("Retry-After")

                        if retry_after:
                            try:
                                wait = float(retry_after)
                            except ValueError:
                                wait = min(2 ** attempt + random.random(), 30)
                        else:
                            wait = min(2 ** attempt + random.random(), 30)

                        if attempt == attempts - 1:
                            log.error(
                                "HTTP %s after retries: %s",
                                response.status,
                                url
                            )
                            return None

                        log.warning(
                            "HTTP %s for %s. Retrying in %.1f seconds.",
                            response.status,
                            url,
                            wait
                        )

                        await asyncio.sleep(wait)
                        continue

                    # Other HTTP errors
                    response.raise_for_status()

            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:

                if attempt == attempts - 1:
                    log.error(
                        "Request failed for %s: %s",
                        url,
                        exc
                    )
                    return None

                wait = min(2 ** attempt + random.random(), 20)

                log.warning(
                    "Request error for %s. Retrying in %.1f seconds.",
                    url,
                    wait
                )

                await asyncio.sleep(wait)

        return None
