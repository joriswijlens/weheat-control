"""Heat the tank to 55 C between 02:00 and 05:00, every day.

Writes to the heat pump. The safety floor of 40 C keeps the tank usable
outside those hours, and the weekly legionella cycle is left alone.
"""

import asyncio

from weheat_control import (
    DEFAULT_HOST,
    HeatPumpSettings,
    InstallationDiscovery,
    access_token,
    day_schedule,
    every_day,
)


async def main() -> None:
    token = access_token()
    info = (await InstallationDiscovery.async_discover(DEFAULT_HOST, token))[0]
    pump = HeatPumpSettings(DEFAULT_HOST, info.installation_id, info.control_board_id)

    night = day_schedule({(2, 5): 55})
    await pump.async_set_dhw_schedule(
        token, every_day(night), enabled=True, safety_temperature=40)
    print("schedule written")


asyncio.run(main())
