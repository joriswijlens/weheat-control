"""Unofficial write access to Weheat heat pump settings.

Layout follows the official read-only client `weheat` (wefabricate/wh-python)
so that the two sit side by side, and so that adopting these endpoints upstream
is a matter of widening the OpenAPI spec rather than reshaping an API.
"""

__version__ = "0.1.1"

from .abstractions.discovery import InstallationDiscovery
from .auth import PortalSession, access_token, login, read_credentials
from .abstractions.settings import HeatPumpSettings
from .api.control_board_api import PROTECTED_PREFIXES, ControlBoardApi
from .api.installation_api import InstallationApi
from .api_client import ApiClient
from .api_response import ApiResponse
from .configuration import DEFAULT_HOST, Configuration
from .exceptions import ApiException, ProtectedSettingError, WeheatControlException
from .models.installation_settings_dto import InstallationSettingsDto
from .schedule import BLOCKS_PER_DAY, DAYS, day_schedule, every_day, schedule_settings

__all__ = [
    "ApiClient",
    "access_token",
    "ApiException",
    "ApiResponse",
    "BLOCKS_PER_DAY",
    "Configuration",
    "ControlBoardApi",
    "DAYS",
    "DEFAULT_HOST",
    "HeatPumpSettings",
    "InstallationApi",
    "InstallationDiscovery",
    "InstallationSettingsDto",
    "PROTECTED_PREFIXES",
    "PortalSession",
    "ProtectedSettingError",
    "WeheatControlException",
    "day_schedule",
    "login",
    "read_credentials",
    "every_day",
    "schedule_settings",
]
