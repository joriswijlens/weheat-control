"""Control board endpoints - the write side of the portal API.

Settings are read per installation but written per control board, and the
casing differs: reads return camelCase, writes expect PascalCase.
"""

from __future__ import annotations

from ..api_client import ApiClient
from ..api_response import ApiResponse
from ..exceptions import ProtectedSettingError

#: Installer- and hardware-level fields. Writing these can disable domestic hot
#: water or damage the unit, so they are refused unless explicitly allowed.
PROTECTED_PREFIXES = (
    "DhwLegionella",
    "HpcOt",
    "HpcRequest",
    "CirculationPump",
    "WaterHouseInTemperature",
    "DhwNumberOfSensors",
    "DhwPumpOrValve",
    "HcHeaterPlacement",
    "BufferTankSetting",
    "HybridBoilerType",
    "ControlMethod",
)


class ControlBoardApi:
    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    async def api_v1_control_boards_control_board_id_settings_patch(
        self, control_board_id: str, settings: dict,
        update_immediately: bool = False,
        allow_protected: bool = False,
    ) -> None:
        """Write settings. Keys are PascalCase, e.g. ``DhwTargetTemperature``.

        ``update_immediately=False`` matches what the portal sends: the change
        is picked up on the next sync rather than pushed to the unit at once.
        """
        if not allow_protected:
            for key in settings:
                if key.startswith(PROTECTED_PREFIXES):
                    raise ProtectedSettingError(
                        f"{key} is installer-level; pass allow_protected=True "
                        "if you really mean it"
                    )
        await self.api_client.call_api(
            "PATCH", f"/api/v1/control-boards/{control_board_id}/settings",
            body={"settings": settings, "updateImmediately": update_immediately},
        )

    async def api_v1_control_boards_control_board_id_settings_patch_with_http_info(
        self, control_board_id: str, settings: dict,
        update_immediately: bool = False,
        allow_protected: bool = False,
    ) -> ApiResponse:
        if not allow_protected:
            for key in settings:
                if key.startswith(PROTECTED_PREFIXES):
                    raise ProtectedSettingError(
                        f"{key} is installer-level; pass allow_protected=True "
                        "if you really mean it"
                    )
        return await self.api_client.call_api_with_http_info(
            "PATCH", f"/api/v1/control-boards/{control_board_id}/settings",
            body={"settings": settings, "updateImmediately": update_immediately},
        )
