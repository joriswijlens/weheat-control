"""Configuration for the Weheat portal API.

Mirrors `weheat.configuration.Configuration` from the official read-only
client, so the two can be configured the same way.
"""

from __future__ import annotations

import aiohttp

DEFAULT_HOST = "https://api.weheat.nl"


class Configuration:
    def __init__(self, host: str = DEFAULT_HOST, access_token: str | None = None,
                 client_session: aiohttp.ClientSession | None = None) -> None:
        self.host = host.rstrip("/")
        self.access_token = access_token
        self.client_session = client_session
