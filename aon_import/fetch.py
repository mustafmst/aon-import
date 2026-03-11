from __future__ import annotations

import hashlib
import random
import time
from pathlib import Path

import httpx

from aon_import.config import AppConfig


class Fetcher:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._client = httpx.Client(
            headers={"User-Agent": config.http.user_agent},
            timeout=config.http.timeout_seconds,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Fetcher":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def fetch(self, url: str) -> str:
        self._sleep_between_requests()
        max_attempts = max(1, self.config.http.max_retries)

        for attempt in range(1, max_attempts + 1):
            try:
                response = self._client.get(url)
                response.raise_for_status()
                html = response.text
                self._maybe_cache_raw(url, html)
                return html
            except httpx.HTTPError:
                if attempt >= max_attempts:
                    raise
                time.sleep(self.config.http.backoff_seconds * attempt)

        raise RuntimeError(f"Failed to fetch URL after {max_attempts} attempts: {url}")

    def _sleep_between_requests(self) -> None:
        minimum, maximum = self.config.http.delay_ms
        delay_ms = random.randint(minimum, maximum)
        time.sleep(delay_ms / 1000.0)

    def _maybe_cache_raw(self, url: str, html: str) -> None:
        if not self.config.cache.enabled:
            return

        cache_dir = self.config.cache.raw_html_dir
        cache_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
        cache_path = Path(cache_dir) / f"{digest}.html"
        cache_path.write_text(html, encoding="utf-8")
