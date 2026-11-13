"""Login for the Weheat portal API through the portal's own next-auth session.

Keycloak's `weheat-portal` client no longer works for direct PKCE (it wants a
secret), so we do what the portal's browser does, without a browser: sign in
via next-auth, walk the Keycloak login form, and keep the cookie jar. The
portal's `/api/auth/session` then hands out access tokens; the session lasts
about 30 days and renews tokens without the password.
"""

from __future__ import annotations

import base64
import html
import json
import os
import re
import time
from urllib.parse import urlparse

import requests

PORTAL = "https://portal.weheat.nl"
KEYCLOAK_HOST = "auth.weheat.nl"
TIMEOUT = 30
#: Used when the token carries no readable expiry; Weheat access tokens live 5 min.
TOKEN_LIFETIME = 300

DEFAULT_CREDENTIALS = os.path.expanduser("~/.weheat-credentials")
DEFAULT_CACHE = os.path.expanduser("~/.weheat-token.json")


def read_credentials(path: str = DEFAULT_CREDENTIALS) -> tuple[str, str]:
    """Credentials from the environment, or from a `user=`/`password=` file.

    `WEHEAT_USER` and `WEHEAT_PASSWORD` win when both are set, which is what
    CI uses. File values are taken verbatim after the first `=`, so passwords
    may contain any character.
    """
    env_user, env_password = os.environ.get("WEHEAT_USER"), os.environ.get("WEHEAT_PASSWORD")
    if env_user and env_password:
        return env_user, env_password

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"no credentials: set WEHEAT_USER and WEHEAT_PASSWORD, or create "
            f"{path} with 'user=' and 'password=' lines"
        )

    values: dict[str, str] = {}
    with open(path) as handle:
        for line in handle:
            line = line.rstrip("\n")
            if "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value
    missing = {"user", "password"} - values.keys()
    if missing:
        raise ValueError(f"{path} mist: {', '.join(sorted(missing))}")
    return values["user"], values["password"]


def _user_agent() -> str:
    from . import __version__
    return f"weheat-control/{__version__}"


def _token_expiry(token: str) -> float:
    """The `exp` claim of a JWT, or a five minute guess."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return float(json.loads(base64.urlsafe_b64decode(payload))["exp"])
    except (IndexError, ValueError, KeyError, TypeError):
        return time.time() + TOKEN_LIFETIME


class PortalSession:
    """A logged-in portal session that keeps its cookie jar.

    Network problems propagate as `requests` exceptions; rejected credentials
    raise `RuntimeError`. No Home Assistant imports, so it is usable anywhere.
    """

    def __init__(self, session: requests.Session | None = None, portal: str = PORTAL) -> None:
        self.portal = portal.rstrip("/")
        self.http = session or requests.Session()
        self.http.headers["User-Agent"] = _user_agent()
        self._token: str | None = None
        self._token_expires_at = 0.0

    def login(self, username: str, password: str) -> str:
        """Sign in with the password. Returns a fresh access token."""
        csrf = self.http.get(f"{self.portal}/api/auth/csrf", timeout=TIMEOUT)
        csrf.raise_for_status()
        signin = self.http.post(
            f"{self.portal}/api/auth/signin/keycloak",
            data={"csrfToken": csrf.json()["csrfToken"],
                  "callbackUrl": self.portal, "json": "true"},
            timeout=TIMEOUT,
        )
        signin.raise_for_status()

        page = self.http.get(signin.json()["url"], timeout=TIMEOUT)
        page.raise_for_status()
        # The login page is a JavaScript theme; the POST target lives in kcContext.
        match = re.search(r'"loginAction"\s*:\s*"([^"]+)"', page.text)
        if not match:
            raise RuntimeError("loginAction not found - the login page changed")
        action = html.unescape(match.group(1).replace("\\/", "/"))

        posted = self.http.post(
            action,
            data={"username": username, "password": password, "credentialId": ""},
            timeout=TIMEOUT,
        )
        posted.raise_for_status()
        # A wrong password re-renders the Keycloak form instead of redirecting back.
        if urlparse(posted.url).hostname == KEYCLOAK_HOST:
            raise RuntimeError("login rejected (wrong username or password)")

        token = self._fetch_token()
        if not token:
            raise RuntimeError("login rejected (the portal issued no session)")
        return token

    def _fetch_token(self) -> str | None:
        response = self.http.get(f"{self.portal}/api/auth/session", timeout=TIMEOUT)
        response.raise_for_status()
        token = (response.json() or {}).get("accessToken")
        if token:
            self._token = token
            self._token_expires_at = _token_expiry(token)
        return token or None

    def refresh(self) -> str | None:
        """A new access token from the existing session, or None if it has ended."""
        return self._fetch_token()

    def access_token(self, username: str | None = None, password: str | None = None) -> str:
        """A valid access token: cached, else renewed from the session, else a login."""
        if self._token and self._token_expires_at > time.time() + 30:
            return self._token
        token = self.refresh()
        if token:
            return token
        if username is None or password is None:
            raise RuntimeError("session expired and no credentials given")
        return self.login(username, password)

    def dump(self) -> dict:
        return {"cookies": requests.utils.dict_from_cookiejar(self.http.cookies),
                "access_token": self._token, "expires_at": self._token_expires_at}

    @classmethod
    def load(cls, state: dict, session: requests.Session | None = None) -> "PortalSession":
        restored = cls(session)
        restored.http.cookies = requests.utils.cookiejar_from_dict(state.get("cookies", {}))
        restored._token = state.get("access_token")
        restored._token_expires_at = state.get("expires_at", 0.0)
        return restored


def login(username: str, password: str) -> PortalSession:
    """Log in with the password and return the session (use `.access_token()`)."""
    session = PortalSession()
    session.login(username, password)
    return session


def access_token(
    credentials_path: str = DEFAULT_CREDENTIALS,
    cache_path: str = DEFAULT_CACHE,
) -> str:
    """A valid access token, for the CLI and examples.

    The session cookies are cached, so the password is only used when the
    session has ended (about every 30 days).
    """
    session = None
    if os.path.exists(cache_path):
        try:
            with open(cache_path) as handle:
                session = PortalSession.load(json.load(handle))
        except (ValueError, OSError):
            session = None
    if session is None:
        session = PortalSession()

    token = session.access_token() if session._token else session.refresh()
    if not token:
        token = session.login(*read_credentials(credentials_path))

    with open(cache_path, "w") as handle:
        json.dump(session.dump(), handle)
    os.chmod(cache_path, 0o600)
    return token
