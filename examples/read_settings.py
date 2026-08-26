"""Print the settings that matter for load shifting."""

import asyncio

from weheat_control import (
    DEFAULT_HOST,
    HeatPumpSettings,
    InstallationDiscovery,
    access_token,
)


async def main() -> None:
    token = access_token()
    info = (await InstallationDiscovery.async_discover(DEFAULT_HOST, token))[0]
    pump = HeatPumpSettings(DEFAULT_HOST, info.installation_id, info.control_board_id)
    settings = await pump.async_get_settings(token)

    print(f"hot water target      {settings.dhw_target_temperature} C")
    print(f"schedule enabled      {bool(settings.dhw_schedule_enabled)}")
    print(f"schedule safety floor {settings.dhw_schedule_safety_temperature} C")
    print(f"heating curve         {settings.heating_curve_x} -> {settings.heating_curve_y}")
    print(f"performance preset    {settings.performance_mode_preset}")


asyncio.run(main())
