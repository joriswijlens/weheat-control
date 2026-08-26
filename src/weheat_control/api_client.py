"""Thin async HTTP client shared by the API classes."""

from __future__ import annotations

from typing import Any

import aiohttp

from .api_response import ApiResponse
from .configuration import Configuration
from .exceptions import ApiException


class ApiClient:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self._session = configuration.client_session
        self._owns_session = configuration.client_session is None

    async def __aenter__(self) -> "ApiClient":
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.configuration.access_token:
            headers["Authorization"] = f"Bearer {self.configuration.access_token}"
        return headers

    async def call_api(self, method: str, resource_path: str,
                       params: dict | None = None,
                       body: Any | None = None) -> Any:
        if self._session is None:
            raise RuntimeError("ApiClient must be used as an async context manager")

        headers = self._headers()
        if body is not None:
            headers["Content-Type"] = "application/json"
            # The portal sends this; some deployments check it.
            headers["Origin"] = "https://portal.weheat.nl"

        async with self._session.request(
            method, f"{self.configuration.host}{resource_path}",
            params=params, json=body, headers=headers,
        ) as response:
            text = await response.text()
            if response.status >= 400:
                raise ApiException(response.status, text)
            if not text:
                return None
            return await response.json(content_type=None)

    async def call_api_with_http_info(self, method: str, resource_path: str,
                                      params: dict | None = None,
                                      body: Any | None = None) -> ApiResponse:
        """As `call_api`, but returns status and headers alongside the data.

        The official client offers the same pair; Home Assistant uses the
        `_with_http_info` variants to branch on the status code.
        """
        if self._session is None:
            raise RuntimeError("ApiClient must be used as an async context manager")

        headers = self._headers()
        if body is not None:
            headers["Content-Type"] = "application/json"
            headers["Origin"] = "https://portal.weheat.nl"

        async with self._session.request(
            method, f"{self.configuration.host}{resource_path}",
            params=params, json=body, headers=headers,
        ) as response:
            text = await response.text()
            data = None
            if text:
                try:
                    data = await response.json(content_type=None)
                except Exception:
                    data = None
            return ApiResponse(
                status_code=response.status,
                headers=dict(response.headers),
                data=data,
                raw_data=text,
            )
