import asyncio

import pytest

from weheat_control import ApiException, InstallationDiscovery
from weheat_control.abstractions import discovery
from weheat_control.api_response import ApiResponse


class FakeApi:
    status = 200

    def __init__(self, client): pass

    async def api_v1_installations_fully_expanded_get_with_http_info(self, **kw):
        return ApiResponse(status_code=self.status, data={"data": []}, headers={}, raw_data=b"")


def test_non_200_raises(monkeypatch):
    FakeApi.status = 401
    monkeypatch.setattr(discovery, "InstallationApi", FakeApi)
    with pytest.raises(ApiException) as error:
        asyncio.run(InstallationDiscovery.async_discover("https://x", "t"))
    assert error.value.status == 401
