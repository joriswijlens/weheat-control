"""Login flow against a fake portal + Keycloak (no network)."""

import base64
import json
import time

import pytest
import requests
from requests.adapters import BaseAdapter

from weheat_control.auth import PortalSession


def jwt(exp: float) -> str:
    body = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
    return f"h.{body}.s"


class FakePortal(BaseAdapter):
    """Just enough of next-auth + Keycloak for the happy and sad paths."""

    def __init__(self, password="pw"):
        super().__init__()
        self.password, self.calls, self.tokens, self.logged_in = password, [], [], False

    def close(self):
        pass

    def _response(self, request, status=200, body=b"", headers=None):
        response = requests.Response()
        response.status_code, response._content, response.url = status, body, request.url
        response.headers.update(headers or {})
        response.request = request
        return response

    def send(self, request, **kwargs):
        self.calls.append((request.method, request.url, request.headers.get("User-Agent")))
        url = request.url
        if url.endswith("/api/auth/csrf"):
            return self._response(request, body=b'{"csrfToken": "abc"}')
        if url.endswith("/api/auth/signin/keycloak"):
            return self._response(request, body=b'{"url": "https://auth.weheat.nl/login"}')
        if url == "https://auth.weheat.nl/login":
            return self._response(
                request, body=b'{"loginAction": "https:\\/\\/auth.weheat.nl\\/act?a=1&amp;b=2"}')
        if url.startswith("https://auth.weheat.nl/act"):
            body = request.body if isinstance(request.body, str) else request.body.decode()
            assert "credentialId=" in body
            if f"password={self.password}&" not in body:
                return self._response(request, body=b"login page again")
            self.logged_in = True
            response = self._response(request, body=b"portal home")
            response.url = "https://portal.weheat.nl/"
            self.cookies.set("session", "s1", domain="portal.weheat.nl")
            return response
        if url.endswith("/api/auth/session"):
            ok = "session=s1" in request.headers.get("Cookie", "")
            if not ok:
                return self._response(request, body=b"{}")
            token = self.tokens.pop(0) if self.tokens else jwt(time.time() + 300)
            return self._response(request, body=json.dumps({"accessToken": token}).encode())
        raise AssertionError(url)



def make(portal):
    http = requests.Session()
    portal.cookies = http.cookies
    http.mount("https://", portal)
    return PortalSession(http)


def test_login_returns_token_and_sends_honest_user_agent():
    portal = FakePortal()
    session = make(portal)
    token = session.login("me", "pw")
    assert token.count(".") == 2
    assert all(ua.startswith("weheat-control/") for _, _, ua in portal.calls)
    # loginAction was unescaped
    assert ("POST", "https://auth.weheat.nl/act?a=1&b=2", portal.calls[3][2]) in portal.calls


def test_wrong_password_raises_runtime_error():
    with pytest.raises(RuntimeError, match="rejected"):
        make(FakePortal()).login("me", "wrong")


def test_network_errors_propagate():
    class Down(FakePortal):
        def send(self, request, **kwargs):
            raise requests.ConnectionError("down")

    with pytest.raises(requests.ConnectionError):
        make(Down()).login("me", "pw")


def test_refresh_uses_session_without_password():
    portal = FakePortal()
    session = make(portal)
    session.login("me", "pw")
    portal.calls.clear()
    portal.tokens = [jwt(time.time() + 600)]
    assert session.refresh() is not None
    assert [url.rsplit("/", 1)[-1] for _, url, _ in portal.calls] == ["session"]


def test_access_token_caches_until_expiry_then_renews():
    portal = FakePortal()
    session = make(portal)
    first = session.login("me", "pw")
    portal.calls.clear()
    assert session.access_token() == first and not portal.calls
    session._token_expires_at = 0
    session.access_token()
    assert len(portal.calls) == 1


def test_ended_session_logs_in_again():
    portal = FakePortal()
    session = make(portal)
    session.login("me", "pw")
    session.http.cookies.clear()
    session._token_expires_at = 0
    assert session.access_token("me", "pw")
    with pytest.raises(RuntimeError, match="no credentials"):
        session.http.cookies.clear()
        session._token_expires_at = 0
        session.access_token()


def test_dump_and_load_keep_the_session():
    portal = FakePortal()
    session = make(portal)
    session.login("me", "pw")
    restored = PortalSession.load(session.dump())
    assert restored.http.cookies.get("session") == "s1"
