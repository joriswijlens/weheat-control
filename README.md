# weheat-control

Unofficial Python client for **writing** Weheat heat pump settings: hot water
scheduling, boost, target temperature and the heating curve.

Weheat publishes an official client,
[`wefabricate/wh-python`](https://github.com/wefabricate/wh-python), generated
from their OpenAPI spec. It exposes eight endpoints — heat pumps, logs, energy
logs, user — and all of them are reads. The Home Assistant integration built on
it [states plainly](https://www.home-assistant.io/integrations/weheat/) that
there is no way to control the heat pump.

Meanwhile the Weheat portal, on the same `api.weheat.nl` host and with the same
Keycloak tokens, reads and writes a settings object with 76 fields. This
library talks to those endpoints.

## Why this exists, and when it should stop existing

A heat pump and a hot water tank are the largest shiftable load in most houses.
On a dynamic tariff you want to heat when power is cheap or the panels are
producing — not when the thermostat happens to ask. The Blackbird already has a
quarter-hourly hot water schedule built in. It is off by default and reachable
from nothing but the app.

Every appliance vendor is building a cloud and hoping to become the one that
runs the house. None of them can, because a house is a heat pump and a car
charger and a battery and an inverter from four different vendors, and the
optimisation only works if something sees all of them at once. The parts a
manufacturer is uniquely good at are the driver and the safety envelope: how
the compressor behaves, what the unit must never be asked to do. Scheduling
belongs to whatever the owner points at the whole house — Home Assistant, EVCC,
EMHASS.

So this is not a fork or a protest. It is a request, written in Python:
**publish these endpoints in the OpenAPI spec.** The layout here deliberately
mirrors the official client — `Configuration`, `ApiClient`, generated-style
method names, `*Dto` models, `_with_http_info` variants, an `abstractions/`
layer — so that adopting them upstream is a matter of widening the spec and
regenerating, not of reshaping an API. The day `weheat` ships the settings
endpoints, this package gets a deprecation notice and a pointer to theirs.

## Disclaimer

**Not supported by Weheat. Can break at any moment.** It uses undocumented
endpoints observed in the portal's own traffic, with your own account and your
own credentials. Endpoints, field names and casing can change without notice.
A daily contract check (`.github/workflows/contract.yml`) runs against the live
API so breakage shows up here rather than in your heating schedule.

If your heat pump misbehaves, disable this before contacting Weheat support —
and tell them you were using it. No warranty; see `LICENSE`.

## Install

```bash
pip install -e .
```

Credentials go in `~/.weheat-credentials`, mode 600:

```
user=you@example.com
password=your-portal-password
```

The password is read verbatim after the first `=`, so any character is fine.
`WEHEAT_USER` and `WEHEAT_PASSWORD` override the file, which is what CI uses.

Access tokens last five minutes; the refresh token is cached in
`~/.weheat-token.json`. If you already handle OAuth yourself — as Home
Assistant does — skip `weheat_control.auth` entirely and pass your own token.

## Use

```python
import asyncio

from weheat_control import (
    DEFAULT_HOST, HeatPumpSettings, InstallationDiscovery,
    access_token, day_schedule, every_day,
)


async def main():
    token = access_token()
    info = (await InstallationDiscovery.async_discover(DEFAULT_HOST, token))[0]
    pump = HeatPumpSettings(DEFAULT_HOST, info.installation_id, info.control_board_id)

    settings = await pump.async_get_settings(token)
    print(settings.dhw_target_temperature, settings.dhw_schedule_enabled)

    # Heat the tank to 55 C between 02:00 and 05:00, every day.
    await pump.async_set_dhw_schedule(
        token, every_day(day_schedule({(2, 5): 55})),
        enabled=True, safety_temperature=40,
    )

    # Or heat it right now, for the next two hours.
    await pump.async_boost_dhw(token, minutes=120)


asyncio.run(main())
```

See `examples/` for a settings dump, a night schedule, and the contract check.

## The API

| | |
|---|---|
| Auth | Keycloak at `auth.weheat.nl`, realm `Weheat`, client `weheat-portal`, authorization code + PKCE. Direct grant is disabled |
| Discover | `GET /api/v1/installations/fully-expanded` — yields `id` and `heatPump.controlBoardId` |
| Read | `GET /api/v1/installations/{installationId}/settings` — 76 fields, camelCase |
| Write | `PATCH /api/v1/control-boards/{controlBoardId}/settings` — body `{"settings": {...}, "updateImmediately": false}`, keys **PascalCase** |

Reads address the installation, writes address the control board, and the
casing differs between them. That asymmetry is theirs, not ours.

Settings worth knowing:

| Field | Meaning |
|---|---|
| `DhwScheduleEnabled` | Master switch for the hot water schedule |
| `DhwSchedule{Day}Target` | 96 quarter-hour target temperatures, `0` meaning no demand |
| `DhwScheduleSafetyTemperature` | Floor the schedule never goes below |
| `DhwBoostEndTime` | Heat now, until this timestamp |
| `DhwTargetTemperature` | Standing target outside the schedule |
| `HeatingCurveX` / `HeatingCurveY` | Space heating curve, outdoor °C to flow °C |
| `PerformanceModePreset` | Sound modes 1–5, effectively a power cap |
| `SilentHours{Day}Start` / `Stop` | Scheduled power capping |

## What this will not write

`async_set_settings` refuses installer- and hardware-level fields unless you
pass `allow_protected=True`: `DhwLegionella*`, `HpcOt*`, `CirculationPump*`,
`WaterHouseInTemperatureMax` and friends. Those describe how the unit is
plumbed and how it protects itself. Nothing about load shifting needs them.

Legionella prevention deserves its own warning. The unit runs a weekly cycle
above 60 °C. If it fails, it retries every three hours from day six, escalates
to maximum capacity including the electric element on day seven, and on day
eight raises a fault that **stops hot water heating entirely** until an
installer clears it. Schedule *when* the tank heats. Never suppress *whether*
it does.

## Contract check

`examples/contract_check.py` verifies the API still looks the way this library
assumes, and runs daily in CI. Where the official client covers something it is
the reference — heat pump identity, serial number, hot water capability are
asserted against `weheat`, not against our own guesses. What is left is exactly
the delta this library adds.

It needs `WEHEAT_USER` and `WEHEAT_PASSWORD` as repository secrets:

```bash
gh secret set WEHEAT_USER
gh secret set WEHEAT_PASSWORD
```

It writes nothing.
