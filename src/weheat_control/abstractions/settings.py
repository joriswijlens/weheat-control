"""Heat pump settings abstraction, shaped after `weheat.abstractions.heat_pump`."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import aiohttp

from ..api.control_board_api import ControlBoardApi
from ..api.installation_api import InstallationApi
from ..api_client import ApiClient
from ..configuration import Configuration
from ..models import InstallationSettingsDto
from ..schedule import schedule_settings


class HeatPumpSettings:
    """Read and write the settings of one heat pump.

    Reads address the installation, writes address the control board; both ids
    come from `InstallationDiscovery`.
    """

    def __init__(self, api_url: str, installation_id: str, control_board_id: str,
                 client_session: aiohttp.ClientSession | None = None) -> None:
        self._api_url = api_url
        self._installation_id = installation_id
        self._control_board_id = control_board_id
        self._client = client_session
        self._settings: InstallationSettingsDto | None = None

    @property
    def settings(self) -> InstallationSettingsDto | None:
        """The settings from the last successful read."""
        return self._settings

    def _config(self, access_token: str) -> Configuration:
        return Configuration(host=self._api_url, access_token=access_token,
                             client_session=self._client)

    async def async_get_settings(self, access_token: str) -> InstallationSettingsDto:
        async with ApiClient(configuration=self._config(access_token)) as client:
            response = await InstallationApi(
                client).api_v1_installations_installation_id_settings_get_with_http_info(
                    installation_id=self._installation_id)
            if response.status_code == 200:
                self._settings = response.data
        return self._settings

    async def async_set_settings(self, access_token: str, settings: dict,
                                 update_immediately: bool = False,
                                 allow_protected: bool = False) -> None:
        """Write raw PascalCase settings, e.g. ``{"DhwTargetTemperature": 55}``."""
        async with ApiClient(configuration=self._config(access_token)) as client:
            await ControlBoardApi(
                client).api_v1_control_boards_control_board_id_settings_patch(
                    control_board_id=self._control_board_id,
                    settings=settings,
                    update_immediately=update_immediately,
                    allow_protected=allow_protected)

    async def async_set_dhw_target_temperature(self, access_token: str,
                                               temperature: int) -> None:
        """Standing hot water target, in degrees Celsius."""
        await self.async_set_settings(
            access_token, {"DhwTargetTemperature": temperature})

    async def async_set_dhw_schedule(self, access_token: str,
                                     per_day: dict[str, list[int]],
                                     enabled: bool = True,
                                     safety_temperature: int | None = None) -> None:
        """Set the quarter-hourly hot water schedule.

        Shift *when* the tank heats, never whether it heats at all: the weekly
        legionella cycle escalates and eventually faults if it cannot reach
        temperature, which stops hot water until an installer clears it.
        """
        await self.async_set_settings(
            access_token,
            schedule_settings(per_day, enabled=enabled,
                              safety_temperature=safety_temperature))

    async def async_boost_dhw(self, access_token: str,
                              until: datetime | None = None,
                              minutes: int = 60) -> datetime:
        """Heat the tank now, until `until` (default: `minutes` from now)."""
        if until is None:
            until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        stamp = until.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        await self.async_set_settings(access_token, {"DhwBoostEndTime": stamp})
        return until

    async def async_set_heating_curve(self, access_token: str,
                                      outdoor: list[float],
                                      flow: list[float]) -> None:
        """Space heating curve: outdoor temperatures to flow temperatures."""
        if len(outdoor) != len(flow):
            raise ValueError("outdoor and flow must have the same length")
        await self.async_set_settings(
            access_token, {"HeatingCurveX": outdoor, "HeatingCurveY": flow})

    async def async_set_performance_mode(self, access_token: str,
                                         preset: int) -> None:
        """Sound modes 1-5, which cap output power. 5 is full capacity."""
        await self.async_set_settings(
            access_token, {"PerformanceModePreset": preset})
