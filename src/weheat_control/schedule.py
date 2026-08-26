"""Helpers for the quarter-hourly domestic hot water schedule."""

from __future__ import annotations

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday")

#: The schedule is 96 quarter-hour blocks per day.
BLOCKS_PER_DAY = 96


def day_schedule(blocks: dict[tuple[float, float], int], default: int = 0) -> list[int]:
    """Build one day of 96 values from (start_hour, stop_hour) ranges.

    >>> day_schedule({(2, 5): 55})[7:9]
    [0, 55]
    """
    day = [default] * BLOCKS_PER_DAY
    for (start, stop), temperature in blocks.items():
        for quarter in range(int(start * 4), int(stop * 4)):
            day[quarter % BLOCKS_PER_DAY] = temperature
    return day


def schedule_settings(per_day: dict[str, list[int]], enabled: bool = True,
                      safety_temperature: int | None = None) -> dict:
    """Turn day name -> 96 values into a PascalCase settings payload.

    >>> sorted(schedule_settings({"Monday": [0] * 96}))
    ['DhwScheduleEnabled', 'DhwScheduleMondayTarget']
    """
    settings: dict[str, object] = {"DhwScheduleEnabled": 1 if enabled else 0}
    if safety_temperature is not None:
        settings["DhwScheduleSafetyTemperature"] = safety_temperature
    for day, values in per_day.items():
        if day not in DAYS:
            raise ValueError(f"unknown day {day!r}")
        if len(values) != BLOCKS_PER_DAY:
            raise ValueError(
                f"{day} needs {BLOCKS_PER_DAY} values, got {len(values)}")
        settings[f"DhwSchedule{day}Target"] = values
    return settings


def every_day(values: list[int]) -> dict[str, list[int]]:
    """The same day schedule for all seven days."""
    return {day: values for day in DAYS}
