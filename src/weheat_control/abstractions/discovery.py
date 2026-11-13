"""Installation discovery, shaped after `weheat.abstractions.discovery`."""

from __future__ import annotations

from dataclasses import dataclass

import aiohttp

from ..api.installation_api import InstallationApi
from ..api_client import ApiClient
from ..configuration import Configuration
from ..exceptions import ApiException


class InstallationDiscovery:
    @dataclass
    class InstallationInfo:
        installation_id: str
        control_board_id: str
        heat_pump_id: str
        serial_number: str | None = None
        has_dhw: bool = False

    @staticmethod
    async def async_discover(
        api_url: str, access_token: str,
        client_session: aiohttp.ClientSession | None = None,
    ) -> list["InstallationDiscovery.InstallationInfo"]:
        """Every installation the account can reach that has a control board.

        The control board id is what the write endpoint addresses; the
        installation id is what the read endpoint uses.
        """
        config = Configuration(host=api_url, access_token=access_token,
                               client_session=client_session)
        found: list[InstallationDiscovery.InstallationInfo] = []

        async with ApiClient(configuration=config) as client:
            response = await InstallationApi(
                client).api_v1_installations_fully_expanded_get_with_http_info(
                    page=1, page_size=1000)

            if response.status_code != 200:
                raise ApiException(response.status_code, str(response.data or ""))
            for item in (response.data or {}).get("data", []):
                pump = item.get("heatPump") or {}
                if not pump.get("controlBoardId"):
                    continue
                found.append(InstallationDiscovery.InstallationInfo(
                    installation_id=item["id"],
                    control_board_id=pump["controlBoardId"],
                    heat_pump_id=pump.get("id"),
                    serial_number=pump.get("serialNumber"),
                    has_dhw=pump.get("dhwType") == 1,
                ))
        return found
