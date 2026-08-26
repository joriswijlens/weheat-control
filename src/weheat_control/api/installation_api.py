"""Installation endpoints of the Weheat portal API."""

from __future__ import annotations

from ..api_client import ApiClient
from ..api_response import ApiResponse
from ..models import InstallationSettingsDto


class InstallationApi:
    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    async def api_v1_installations_fully_expanded_get(
        self, page: int = 1, page_size: int = 50,
        household_id: str | None = None,
    ) -> dict:
        params = {"page": page, "pageSize": page_size}
        if household_id:
            params["householdId"] = household_id
        return await self.api_client.call_api(
            "GET", "/api/v1/installations/fully-expanded", params=params)

    async def api_v1_installations_installation_id_settings_get(
        self, installation_id: str,
    ) -> dict:
        return await self.api_client.call_api(
            "GET", f"/api/v1/installations/{installation_id}/settings")

    async def api_v1_installations_fully_expanded_get_with_http_info(
        self, page: int = 1, page_size: int = 50,
        household_id: str | None = None,
    ) -> ApiResponse:
        params = {"page": page, "pageSize": page_size}
        if household_id:
            params["householdId"] = household_id
        return await self.api_client.call_api_with_http_info(
            "GET", "/api/v1/installations/fully-expanded", params=params)

    async def api_v1_installations_installation_id_settings_get_with_http_info(
        self, installation_id: str,
    ) -> ApiResponse:
        response = await self.api_client.call_api_with_http_info(
            "GET", f"/api/v1/installations/{installation_id}/settings")
        if response.status_code == 200 and isinstance(response.data, dict):
            response.data = InstallationSettingsDto.from_dict(response.data)
        return response
