"""Pinned-provider Cognito verification; identity claims never grant application roles.

Only configured URLs are contacted. Keys are bounded/cached, RS256 is fixed, and
ID/access tokens are independently verified against their proper client claims.
This module performs no database work and never logs provider responses or tokens.
"""

import base64
import hashlib
import hmac
import json
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from pydantic import BaseModel, ConfigDict, Field


class ProviderError(Exception):
    def __init__(self, status: int, code: str) -> None:
        self.status, self.code = status, code
        super().__init__(code)


Surface = Literal["web", "mobile_web", "native"]


class ProviderClient(BaseModel):
    model_config = ConfigDict(extra="forbid")
    client_id: str = Field(min_length=1, max_length=128)
    redirect_uri: str = Field(min_length=1, max_length=1000)
    return_uri: str | None = Field(default=None, max_length=1000)


class ProviderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    label_en: str = Field(default="Nursery account", min_length=1, max_length=100)
    label_ar: str = Field(default="حساب الحضانة", min_length=1, max_length=100)
    issuer: str = Field(min_length=1, max_length=500)
    domain: str = Field(min_length=1, max_length=500)
    clients: dict[Surface, ProviderClient]


@dataclass(frozen=True, repr=False)
class VerifiedIdentity:
    issuer: str
    subject: str
    expires_at: datetime
    authenticated_at: datetime
    email: str | None
    email_verified: bool


def validate_url(value: str, *, loopback: bool = False, native: bool = False) -> None:
    parsed = urlsplit(value)
    if (
        parsed.username
        or parsed.password
        or "?" in value
        or "#" in value
        or any(ord(char) < 33 for char in value)
    ):
        raise ValueError("Provider URLs must not contain credentials, query or fragment")
    if native and parsed.scheme not in {"http", "https"}:
        if "." not in parsed.scheme or parsed.scheme in {"javascript", "data", "file", "blob"}:
            raise ValueError("Native callback must use an application URI scheme")
        return
    if parsed.scheme == "https" and parsed.hostname:
        return
    if loopback and parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1"}:
        return
    raise ValueError("HTTPS is required; HTTP loopback is allowed only for explicit local fixtures")


def bounded_json(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    data: dict[str, str] | None = None,
    authentication: bool = False,
) -> dict[str, Any]:
    """Per-I/O timeouts plus an overall streaming deadline and 256KiB body bound."""
    deadline = time.monotonic() + 10
    try:
        with client.stream(method, url, data=data, follow_redirects=False) as response:
            if response.status_code != 200:
                raise ProviderError(
                    401 if authentication and response.status_code in {400, 401} else 503,
                    "provider_authentication_failed"
                    if authentication and response.status_code in {400, 401}
                    else "identity_provider_unavailable",
                )
            content = bytearray()
            for chunk in response.iter_bytes():
                content.extend(chunk)
                if len(content) > 262144 or time.monotonic() > deadline:
                    raise ProviderError(503, "identity_provider_unavailable")
            value = json.loads(content)
            if not isinstance(value, dict):
                raise ProviderError(503, "identity_provider_unavailable")
            return value
    except (httpx.HTTPError, ValueError, RecursionError) as error:
        raise ProviderError(503, "identity_provider_unavailable") from error


@dataclass
class CognitoVerifier:
    config: ProviderConfig
    client: httpx.Client = field(repr=False)
    allow_http_loopback: bool = False
    _keys: dict[str, RSAPublicKey] = field(default_factory=dict, repr=False)
    _fetched_at: float = field(default=-1000, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __post_init__(self) -> None:
        validate_url(self.config.issuer, loopback=self.allow_http_loopback)
        validate_url(self.config.domain, loopback=self.allow_http_loopback)
        if urlsplit(self.config.domain).path not in {"", "/"}:
            raise ValueError("Provider domain must have no path")
        if not self.config.clients:
            raise ValueError("At least one provider client is required")
        for surface, client in self.config.clients.items():
            validate_url(
                client.redirect_uri, loopback=self.allow_http_loopback, native=surface == "native"
            )
            if surface != "native":
                if client.return_uri is None:
                    raise ValueError("Browser clients require a fixed return URI")
                validate_url(client.return_uri, loopback=self.allow_http_loopback)

    def key(self, token: str) -> RSAPublicKey:
        try:
            if len(token) > 16384:
                raise ValueError("Oversized token")
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            if header.get("alg") != "RS256" or not isinstance(kid, str) or not 1 <= len(kid) <= 160:
                raise ValueError("Invalid signing-key hint")
        except (jwt.PyJWTError, ValueError, RecursionError) as error:
            raise ProviderError(401, "invalid_provider_token") from error
        if not self._lock.acquire(timeout=5):
            raise ProviderError(503, "identity_provider_unavailable")
        try:
            elapsed = time.monotonic() - self._fetched_at
            if elapsed >= 300 or (kid not in self._keys and elapsed >= 30):
                document = bounded_json(
                    self.client, "GET", self.config.issuer.rstrip("/") + "/.well-known/jwks.json"
                )
                raw = document.get("keys")
                if not isinstance(raw, list) or not 1 <= len(raw) <= 10:
                    raise ProviderError(503, "identity_provider_unavailable")
                keys: dict[str, RSAPublicKey] = {}
                try:
                    for item in raw:
                        if (
                            not isinstance(item, dict)
                            or item.get("kty") != "RSA"
                            or item.get("use") != "sig"
                            or item.get("alg") != "RS256"
                        ):
                            raise ValueError("Invalid provider key")
                        key_id = item.get("kid")
                        if (
                            not isinstance(key_id, str)
                            or not 1 <= len(key_id) <= 160
                            or key_id in keys
                        ):
                            raise ValueError("Invalid provider key identifier")
                        key = jwt.PyJWK.from_dict(item, algorithm="RS256").key
                        if not isinstance(key, RSAPublicKey) or not 2048 <= key.key_size <= 4096:
                            raise ValueError("Unsupported provider signing key")
                        keys[key_id] = key
                except (jwt.PyJWTError, ValueError, TypeError) as error:
                    raise ProviderError(503, "identity_provider_unavailable") from error
                self._keys = keys
                self._fetched_at = time.monotonic()
            if kid not in self._keys:
                raise ProviderError(401, "invalid_provider_token")
            return self._keys[kid]
        finally:
            self._lock.release()

    def claims(self, token: str, client_id: str, use: Literal["id", "access"]) -> dict[str, Any]:
        try:
            claims: dict[str, Any] = jwt.decode(
                token,
                self.key(token),
                algorithms=["RS256"],
                issuer=self.config.issuer,
                audience=client_id if use == "id" else None,
                options={
                    "require": ["exp", "iat", "iss", "sub", "auth_time", "token_use"],
                    "verify_aud": use == "id",
                    "strict_aud": True,
                },
            )
            if claims["token_use"] != use or (
                use == "access" and claims.get("client_id") != client_id
            ):
                raise ValueError("Wrong token purpose or client")
            if any(type(claims[name]) is not int for name in ("exp", "iat", "auth_time")):
                raise ValueError("Invalid token time")
            if (
                not 0
                < claims["auth_time"]
                <= claims["iat"]
                < claims["exp"]
                <= claims["iat"] + 86400
            ):
                raise ValueError("Invalid token lifetime")
            if not isinstance(claims["sub"], str) or not 1 <= len(claims["sub"]) <= 255:
                raise ValueError("Invalid subject")
            return claims
        except (jwt.PyJWTError, ValueError, TypeError, OverflowError) as error:
            raise ProviderError(401, "invalid_provider_token") from error

    def verify_pair(
        self, id_token: str, access_token: str, surface: Surface, nonce: str
    ) -> VerifiedIdentity:
        config = self.config.clients.get(surface)
        if config is None:
            raise ProviderError(400, "identity_client_unavailable")
        identity = self.claims(id_token, config.client_id, "id")
        access = self.claims(access_token, config.client_id, "access")
        actual_nonce = identity.get("nonce")
        if (
            not isinstance(actual_nonce, str)
            or not actual_nonce.isascii()
            or len(actual_nonce) > 256
            or not hmac.compare_digest(actual_nonce, nonce)
            or identity["sub"] != access["sub"]
            or identity["auth_time"] != access["auth_time"]
        ):
            raise ProviderError(401, "invalid_provider_token")
        scopes = access.get("scope")
        if not isinstance(scopes, str) or "openid" not in scopes.split():
            raise ProviderError(401, "invalid_provider_token")
        expected_hash = (
            base64.urlsafe_b64encode(hashlib.sha256(access_token.encode()).digest()[:16])
            .rstrip(b"=")
            .decode()
        )
        if "at_hash" in identity and (
            not isinstance(identity["at_hash"], str)
            or not identity["at_hash"].isascii()
            or not hmac.compare_digest(identity["at_hash"], expected_hash)
        ):
            raise ProviderError(401, "invalid_provider_token")
        email = identity.get("email")
        return VerifiedIdentity(
            self.config.issuer,
            identity["sub"],
            datetime.fromtimestamp(min(identity["exp"], access["exp"]), UTC),
            datetime.fromtimestamp(identity["auth_time"], UTC),
            email if isinstance(email, str) else None,
            identity.get("email_verified") is True,
        )
