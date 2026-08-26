"""Settings of one installation, as returned by the portal API.

Generated from a live response; field names follow the OpenAPI generator's
conventions so this drops in alongside the official client's models.
"""

from __future__ import annotations

import json
import pprint
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Set, Union

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing_extensions import Self


class InstallationSettingsDto(BaseModel):
    """InstallationSettingsDto"""

    control_method: Optional[StrictInt] = Field(default=None, alias="controlMethod")
    hybrid_boiler_type: Optional[StrictInt] = Field(default=None, alias="hybridBoilerType")
    heating_curve_x: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="heatingCurveX")
    heating_curve_y: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="heatingCurveY")
    dhw_target_temperature: Optional[StrictInt] = Field(default=None, alias="dhwTargetTemperature")
    dhw_legionella_target_temperature: Optional[StrictInt] = Field(default=None, alias="dhwLegionellaTargetTemperature")
    dhw_available: Optional[StrictInt] = Field(default=None, alias="dhwAvailable")
    dhw_legionella_prevention: Optional[StrictInt] = Field(default=None, alias="dhwLegionellaPrevention")
    dhw_legionella_start_hour: Optional[StrictInt] = Field(default=None, alias="dhwLegionellaStartHour")
    dhw_legionella_start_day: Optional[StrictInt] = Field(default=None, alias="dhwLegionellaStartDay")
    dhw_pump_or_valve: Optional[StrictInt] = Field(default=None, alias="dhwPumpOrValve")
    circulation_pump_ch_control_type: Optional[StrictInt] = Field(default=None, alias="circulationPumpChControlType")
    circulation_pump_dhw_control_type: Optional[StrictInt] = Field(default=None, alias="circulationPumpDhwControlType")
    water_house_in_temperature_max: Optional[StrictInt] = Field(default=None, alias="waterHouseInTemperatureMax")
    hpc_ot_max_thermostat_setpoint: Optional[StrictInt] = Field(default=None, alias="hpcOtMaxThermostatSetpoint")
    circulation_pump_ch_target_flow: Optional[StrictInt] = Field(default=None, alias="circulationPumpChTargetFlow")
    circulation_pump_dhw_target_flow: Optional[StrictInt] = Field(default=None, alias="circulationPumpDhwTargetFlow")
    circulation_pump_ch_target_flow_silent: Optional[StrictInt] = Field(default=None, alias="circulationPumpChTargetFlowSilent")
    circulation_pump_dhw_target_flow_silent: Optional[StrictInt] = Field(default=None, alias="circulationPumpDhwTargetFlowSilent")
    hpc_ot_thermostat_ignore_status: Optional[StrictInt] = Field(default=None, alias="hpcOtThermostatIgnoreStatus")
    hpc_request_legionella_run_time: Optional[datetime] = Field(default=None, alias="hpcRequestLegionellaRunTime")
    dhw_boost_end_time: Optional[datetime] = Field(default=None, alias="dhwBoostEndTime")
    dhw_number_of_sensors: Optional[StrictInt] = Field(default=None, alias="dhwNumberOfSensors")
    hc_heater_placement: Optional[StrictInt] = Field(default=None, alias="hcHeaterPlacement")
    hc_error_only: Optional[StrictInt] = Field(default=None, alias="hcErrorOnly")
    buffer_tank_setting: Optional[StrictInt] = Field(default=None, alias="bufferTankSetting")
    silent_hours_monday_start: Optional[StrictInt] = Field(default=None, alias="silentHoursMondayStart")
    silent_hours_monday_stop: Optional[StrictInt] = Field(default=None, alias="silentHoursMondayStop")
    silent_hours_tuesday_start: Optional[StrictInt] = Field(default=None, alias="silentHoursTuesdayStart")
    silent_hours_tuesday_stop: Optional[StrictInt] = Field(default=None, alias="silentHoursTuesdayStop")
    silent_hours_wednesday_start: Optional[StrictInt] = Field(default=None, alias="silentHoursWednesdayStart")
    silent_hours_wednesday_stop: Optional[StrictInt] = Field(default=None, alias="silentHoursWednesdayStop")
    silent_hours_thursday_start: Optional[StrictInt] = Field(default=None, alias="silentHoursThursdayStart")
    silent_hours_thursday_stop: Optional[StrictInt] = Field(default=None, alias="silentHoursThursdayStop")
    silent_hours_friday_start: Optional[StrictInt] = Field(default=None, alias="silentHoursFridayStart")
    silent_hours_friday_stop: Optional[StrictInt] = Field(default=None, alias="silentHoursFridayStop")
    silent_hours_saturday_start: Optional[StrictInt] = Field(default=None, alias="silentHoursSaturdayStart")
    silent_hours_saturday_stop: Optional[StrictInt] = Field(default=None, alias="silentHoursSaturdayStop")
    silent_hours_sunday_start: Optional[StrictInt] = Field(default=None, alias="silentHoursSundayStart")
    silent_hours_sunday_stop: Optional[StrictInt] = Field(default=None, alias="silentHoursSundayStop")
    silent_minutes_monday_start: Optional[StrictInt] = Field(default=None, alias="silentMinutesMondayStart")
    silent_minutes_monday_stop: Optional[StrictInt] = Field(default=None, alias="silentMinutesMondayStop")
    silent_minutes_tuesday_start: Optional[StrictInt] = Field(default=None, alias="silentMinutesTuesdayStart")
    silent_minutes_tuesday_stop: Optional[StrictInt] = Field(default=None, alias="silentMinutesTuesdayStop")
    silent_minutes_wednesday_start: Optional[StrictInt] = Field(default=None, alias="silentMinutesWednesdayStart")
    silent_minutes_wednesday_stop: Optional[StrictInt] = Field(default=None, alias="silentMinutesWednesdayStop")
    silent_minutes_thursday_start: Optional[StrictInt] = Field(default=None, alias="silentMinutesThursdayStart")
    silent_minutes_thursday_stop: Optional[StrictInt] = Field(default=None, alias="silentMinutesThursdayStop")
    silent_minutes_friday_start: Optional[StrictInt] = Field(default=None, alias="silentMinutesFridayStart")
    silent_minutes_friday_stop: Optional[StrictInt] = Field(default=None, alias="silentMinutesFridayStop")
    silent_minutes_saturday_start: Optional[StrictInt] = Field(default=None, alias="silentMinutesSaturdayStart")
    silent_minutes_saturday_stop: Optional[StrictInt] = Field(default=None, alias="silentMinutesSaturdayStop")
    silent_minutes_sunday_start: Optional[StrictInt] = Field(default=None, alias="silentMinutesSundayStart")
    silent_minutes_sunday_stop: Optional[StrictInt] = Field(default=None, alias="silentMinutesSundayStop")
    cooling_control_method: Optional[StrictInt] = Field(default=None, alias="coolingControlMethod")
    cooling_enabled: Optional[StrictInt] = Field(default=None, alias="coolingEnabled")
    cooling_min_setpoint: Optional[StrictInt] = Field(default=None, alias="coolingMinSetpoint")
    input_contact_setting: Optional[StrictInt] = Field(default=None, alias="inputContactSetting")
    cooling_curve_x: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="coolingCurveX")
    cooling_curve_y: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="coolingCurveY")
    consumer_cooling_setpoint: Optional[StrictInt] = Field(default=None, alias="consumerCoolingSetpoint")
    performance_mode_preset: Optional[StrictInt] = Field(default=None, alias="performanceModePreset")
    silent_hours_scheduled_preset: Optional[StrictInt] = Field(default=None, alias="silentHoursScheduledPreset")
    cloud_thermostat_pid_p: Optional[StrictInt] = Field(default=None, alias="cloudThermostatPidP")
    cloud_thermostat_pid_i: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="cloudThermostatPidI")
    cloud_thermostat_pid_d: Optional[StrictInt] = Field(default=None, alias="cloudThermostatPidD")
    cloud_thermostat_heating_curve_y: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="cloudThermostatHeatingCurveY")
    dhw_schedule_enabled: Optional[StrictInt] = Field(default=None, alias="dhwScheduleEnabled")
    dhw_schedule_safety_temperature: Optional[StrictInt] = Field(default=None, alias="dhwScheduleSafetyTemperature")
    dhw_schedule_monday_target: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="dhwScheduleMondayTarget")
    dhw_schedule_tuesday_target: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="dhwScheduleTuesdayTarget")
    dhw_schedule_wednesday_target: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="dhwScheduleWednesdayTarget")
    dhw_schedule_thursday_target: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="dhwScheduleThursdayTarget")
    dhw_schedule_friday_target: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="dhwScheduleFridayTarget")
    dhw_schedule_saturday_target: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="dhwScheduleSaturdayTarget")
    dhw_schedule_sunday_target: Optional[List[Union[StrictFloat, StrictInt]]] = Field(default=None, alias="dhwScheduleSundayTarget")

    __properties: ClassVar[List[str]] = ["control_method", "hybrid_boiler_type", "heating_curve_x", "heating_curve_y", "dhw_target_temperature", "dhw_legionella_target_temperature", "dhw_available", "dhw_legionella_prevention", "dhw_legionella_start_hour", "dhw_legionella_start_day", "dhw_pump_or_valve", "circulation_pump_ch_control_type", "circulation_pump_dhw_control_type", "water_house_in_temperature_max", "hpc_ot_max_thermostat_setpoint", "circulation_pump_ch_target_flow", "circulation_pump_dhw_target_flow", "circulation_pump_ch_target_flow_silent", "circulation_pump_dhw_target_flow_silent", "hpc_ot_thermostat_ignore_status", "hpc_request_legionella_run_time", "dhw_boost_end_time", "dhw_number_of_sensors", "hc_heater_placement", "hc_error_only", "buffer_tank_setting", "silent_hours_monday_start", "silent_hours_monday_stop", "silent_hours_tuesday_start", "silent_hours_tuesday_stop", "silent_hours_wednesday_start", "silent_hours_wednesday_stop", "silent_hours_thursday_start", "silent_hours_thursday_stop", "silent_hours_friday_start", "silent_hours_friday_stop", "silent_hours_saturday_start", "silent_hours_saturday_stop", "silent_hours_sunday_start", "silent_hours_sunday_stop", "silent_minutes_monday_start", "silent_minutes_monday_stop", "silent_minutes_tuesday_start", "silent_minutes_tuesday_stop", "silent_minutes_wednesday_start", "silent_minutes_wednesday_stop", "silent_minutes_thursday_start", "silent_minutes_thursday_stop", "silent_minutes_friday_start", "silent_minutes_friday_stop", "silent_minutes_saturday_start", "silent_minutes_saturday_stop", "silent_minutes_sunday_start", "silent_minutes_sunday_stop", "cooling_control_method", "cooling_enabled", "cooling_min_setpoint", "input_contact_setting", "cooling_curve_x", "cooling_curve_y", "consumer_cooling_setpoint", "performance_mode_preset", "silent_hours_scheduled_preset", "cloud_thermostat_pid_p", "cloud_thermostat_pid_i", "cloud_thermostat_pid_d", "cloud_thermostat_heating_curve_y", "dhw_schedule_enabled", "dhw_schedule_safety_temperature", "dhw_schedule_monday_target", "dhw_schedule_tuesday_target", "dhw_schedule_wednesday_target", "dhw_schedule_thursday_target", "dhw_schedule_friday_target", "dhw_schedule_saturday_target", "dhw_schedule_sunday_target"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of InstallationSettingsDto from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias"""
        excluded_fields: Set[str] = set()
        return self.model_dump(by_alias=True, exclude=excluded_fields, exclude_none=True)

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of InstallationSettingsDto from a dict"""
        if obj is None:
            return None
        if not isinstance(obj, dict):
            return cls.model_validate(obj)
        return cls.model_validate(obj)
