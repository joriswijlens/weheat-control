"""Read-only check that the portal API still behaves as this library expects.

Where the official client `weheat` (wefabricate/wh-python) covers something, it
is the reference: we assert our view against theirs rather than against our own
assumptions. What remains is exactly the delta this library adds - the settings
endpoints their OpenAPI spec does not expose.

Read-only by default, so it is safe as a cron job and safe in CI. Pass
``--write`` to also prove the write path: it reads the hot water target and
writes back the value it just read, which changes nothing but does exercise
the PATCH.
"""

import asyncio
import sys

from weheat import DeviceState
from weheat.abstractions.discovery import HeatPumpDiscovery

from weheat_control import (
    DEFAULT_HOST,
    HeatPumpSettings,
    InstallationDiscovery,
    ProtectedSettingError,
    access_token,
)

#: Settings fields this library builds on. Absent from the official spec, so
#: there is nothing upstream to check them against.
EXPECTED_FIELDS = (
    "dhw_schedule_enabled",
    "dhw_schedule_safety_temperature",
    "dhw_schedule_monday_target",
    "dhw_boost_end_time",
    "dhw_target_temperature",
    "heating_curve_x",
    "heating_curve_y",
    "performance_mode_preset",
)

BLOCKS_PER_DAY = 96

failures = 0


def check(condition: bool, message: str) -> None:
    global failures
    print(f"{'ok  ' if condition else 'FAIL'} {message}")
    failures += not condition


async def main() -> int:
    token = access_token()

    # The official client is the reference for anything it covers.
    official = await HeatPumpDiscovery.async_discover_active(DEFAULT_HOST, token)
    check(bool(official), "official client: heat pumps discovered")
    if not official:
        return 1
    reference = official[0]

    ours = await InstallationDiscovery.async_discover(DEFAULT_HOST, token)
    check(bool(ours), "this client: installations with a control board discovered")
    if not ours:
        return 1
    info = ours[0]

    known = {pump.uuid for pump in official}
    check(info.heat_pump_id in known,
          "heat pump id agrees with the official client")
    check(info.serial_number == reference.sn,
          f"serial number agrees ({info.serial_number})")
    check(info.has_dhw == reference.has_dhw,
          f"domestic hot water flag agrees ({info.has_dhw})")

    # From here on we are past what the official spec exposes.
    pump = HeatPumpSettings(DEFAULT_HOST, info.installation_id, info.control_board_id)
    settings = await pump.async_get_settings(token)
    check(settings is not None, "settings endpoint readable")
    if settings is None:
        return 1

    missing = [f for f in EXPECTED_FIELDS if getattr(settings, f, None) is None]
    check(not missing,
          f"all {len(EXPECTED_FIELDS)} expected fields present"
          + (f" (missing: {', '.join(missing)})" if missing else ""))

    blocks = len(settings.dhw_schedule_monday_target or [])
    check(blocks == BLOCKS_PER_DAY,
          f"hot water schedule has {blocks} quarter-hour blocks")

    try:
        await pump.async_set_settings(token, {"DhwLegionellaPrevention": 0})
    except ProtectedSettingError:
        check(True, "installer-level writes refused")
    else:
        check(False, "installer-level write was NOT refused")

    if "--write" in sys.argv:
        await check_write(pump, token, settings.dhw_target_temperature)

    return 1 if failures else 0


async def check_write(pump: HeatPumpSettings, token: str, current: int) -> None:
    """Write back the value we just read: a no-op that still exercises PATCH."""
    try:
        await pump.async_set_dhw_target_temperature(token, current)
    except Exception as error:
        check(False, f"write refused: {error}")
        return
    check(True, f"write accepted (hot water target rewritten as {current} C)")

    after = await pump.async_get_settings(token)
    check(after.dhw_target_temperature == current,
          f"value unchanged after write ({after.dhw_target_temperature} C)")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
