"""Keycloak login for the Weheat portal API.

The portal uses authorization code + PKCE against a public client. Direct
grant is disabled, so we walk the login form server-side instead of opening a
browser. Tokens are cached and refreshed.
"""

from __future__ import annotations

import base64
import hashlib
import html
import json
import os
import re
import secrets
import time
from urllib.parse import parse_qs, urlparse

import requests

AUTH = "https://auth.weheat.nl/realms/Weheat/protocol/openid-connect"
CLIENT_ID = "weheat-portal"
REDIRECT = "https://portal.weheat.nl/api/auth/callback/keycloak"

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


def _pkce() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode().rstrip("=")
    digest = hashlib.sha256(verifier.encode()).digest()
    return verifier, base64.urlsafe_b64encode(digest).decode().rstrip("=")


def login(username: str, password: str) -> dict:
    """Full authorization code flow. Returns the raw token response."""
    verifier, challenge = _pkce()
    session = requests.Session()

    page = session.get(
        f"{AUTH}/auth",
        params={
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT,
            "response_type": "code",
            "scope": "openid email profile offline_access",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": secrets.token_urlsafe(16),
        },
        timeout=30,
    )
    page.raise_for_status()

    # The login page is a JavaScript theme; the POST target lives in kcContext.
    match = re.search(r'"loginAction"\s*:\s*"([^"]+)"', page.text)
    if not match:
        raise RuntimeError("loginAction not found - the login page changed")
    action = html.unescape(match.group(1).replace("\\/", "/"))

    posted = session.post(
        action,
        data={"username": username, "password": password, "credentialId": ""},
        allow_redirects=False,
        timeout=30,
    )
    location = posted.headers.get("location", "")
    if "code=" not in location:
        raise RuntimeError(f"login rejected (HTTP {posted.status_code})")
    code = parse_qs(urlparse(location).query)["code"][0]

    tokens = session.post(
        f"{AUTH}/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT,
            "client_id": CLIENT_ID,
            "code_verifier": verifier,
        },
        timeout=30,
    )
    tokens.raise_for_status()
    return tokens.json()


def refresh(tokens: dict) -> dict | None:
    response = requests.post(
        f"{AUTH}/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "client_id": CLIENT_ID,
        },
        timeout=30,
    )
    return response.json() if response.status_code == 200 else None


def access_token(
    credentials_path: str = DEFAULT_CREDENTIALS,
    cache_path: str = DEFAULT_CACHE,
) -> str:
    """A valid access token, refreshed or re-obtained as needed.

    Access tokens live five minutes, so caching the refresh token keeps the
    password out of the hot path.
    """
    tokens = None
    if os.path.exists(cache_path):
        with open(cache_path) as handle:
            tokens = json.load(handle)
        if tokens.get("expires_at", 0) > time.time() + 30:
            return tokens["access_token"]
        tokens = refresh(tokens)
    if not tokens:
        tokens = login(*read_credentials(credentials_path))

    tokens["expires_at"] = time.time() + tokens.get("expires_in", 300)
    with open(cache_path, "w") as handle:
        json.dump(tokens, handle)
    os.chmod(cache_path, 0o600)
    return tokens["access_token"]
