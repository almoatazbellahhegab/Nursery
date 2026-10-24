"""Real RSA-signed provider fixtures; no live provider, private-key fixture or user data."""

import json
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from nursery_api.runtime.oidc_verifier import CognitoVerifier, ProviderConfig, ProviderError


@dataclass(repr=False)
class SignedProvider:
    verifier: CognitoVerifier
    id_key: rsa.RSAPrivateKey = field(repr=False)
    access_key: rsa.RSAPrivateKey = field(repr=False)
    document: dict[str, Any] = field(repr=False)
    requests: list[httpx.Request] = field(repr=False)

    def pair(
        self, *, identity: dict[str, Any] | None = None, access: dict[str, Any] | None = None
    ) -> tuple[str, str]:
        now = int(time.time())
        common = {
            "iss": "https://issuer.example.test/pool",
            "sub": "synthetic-provider-subject",
            "auth_time": now - 30,
            "iat": now - 5,
            "exp": now + 300,
        }
        first = {
            **common,
            "token_use": "id",
            "aud": "synthetic-web-client",
            "nonce": "synthetic-nonce",
            "email": "fixture@example.test",
            "email_verified": True,
            **(identity or {}),
        }
        second = {
            **common,
            "token_use": "access",
            "client_id": "synthetic-web-client",
            "scope": "openid email",
            **(access or {}),
        }
        return (
            jwt.encode(first, self.id_key, algorithm="RS256", headers={"kid": "id-key"}),
            jwt.encode(second, self.access_key, algorithm="RS256", headers={"kid": "access-key"}),
        )


@pytest.fixture
def signed() -> Any:
    keys = [rsa.generate_private_key(public_exponent=65537, key_size=2048) for _ in range(2)]
    public = []
    for name, key in zip(("id-key", "access-key"), keys, strict=True):
        item = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
        public.append({**item, "kid": name, "alg": "RS256", "use": "sig"})
    document = {"keys": public}
    requests = []

    def serve(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=document)

    config = ProviderConfig.model_validate(
        {
            "name": "nursery",
            "issuer": "https://issuer.example.test/pool",
            "domain": "https://login.example.test",
            "clients": {
                "web": {
                    "client_id": "synthetic-web-client",
                    "redirect_uri": "https://app.example.test/api/v1/auth/oidc/callback",
                    "return_uri": "https://app.example.test/",
                },
                "native": {
                    "client_id": "synthetic-native-client",
                    "redirect_uri": "com.example.nursery:/oauthredirect",
                },
            },
        }
    )
    with httpx.Client(transport=httpx.MockTransport(serve), timeout=5) as client:
        yield SignedProvider(CognitoVerifier(config, client), keys[0], keys[1], document, requests)


def test_oidc_001_independent_signatures_identity_and_cached_pinned_keys(
    signed: SignedProvider,
) -> None:
    pair = signed.pair(identity={"role": "administrator", "organization_id": "forged"})
    result = signed.verifier.verify_pair(*pair, "web", "synthetic-nonce")
    assert result.subject == "synthetic-provider-subject" and result.email_verified
    assert not hasattr(result, "role") and not hasattr(result, "organization_id")
    signed.verifier.verify_pair(*pair, "web", "synthetic-nonce")
    assert len(signed.requests) == 1
    assert str(signed.requests[0].url) == "https://issuer.example.test/pool/.well-known/jwks.json"
    assert "authorization" not in signed.requests[0].headers


@pytest.mark.parametrize(
    ("which", "changes"),
    [
        ("id", {"iss": "https://foreign.example.test/pool"}),
        ("id", {"aud": "foreign-client"}),
        ("id", {"aud": ["synthetic-web-client"]}),
        ("id", {"token_use": "access"}),
        ("id", {"nonce": "foreign-nonce"}),
        ("id", {"nonce": "غير صالح"}),
        ("id", {"at_hash": "غير صالح"}),
        ("id", {"exp": 1}),
        ("id", {"iat": 9999999999}),
        ("id", {"auth_time": True}),
        ("id", {"sub": ""}),
        ("access", {"client_id": "foreign-client"}),
        ("access", {"token_use": "id"}),
        ("access", {"sub": "other-subject"}),
        ("access", {"auth_time": 1}),
        ("access", {"scope": "email"}),
        ("access", {"exp": 1e100}),
    ],
)
def test_oidc_002_forged_or_inconsistent_claims_fail_closed(
    signed: SignedProvider, which: str, changes: dict[str, Any]
) -> None:
    pair = signed.pair(
        identity=changes if which == "id" else None, access=changes if which == "access" else None
    )
    with pytest.raises(ProviderError) as error:
        signed.verifier.verify_pair(*pair, "web", "synthetic-nonce")
    assert error.value.status == 401


def test_oidc_003_wrong_signature_and_wrong_algorithm_are_rejected(signed: SignedProvider) -> None:
    first, second = signed.pair()
    claims = jwt.decode(first, options={"verify_signature": False})
    forged = jwt.encode(claims, signed.access_key, algorithm="RS256", headers={"kid": "id-key"})
    with pytest.raises(ProviderError):
        signed.verifier.verify_pair(forged, second, "web", "synthetic-nonce")
    symmetric = jwt.encode(
        claims,
        "synthetic-noncredential-signing-material",
        algorithm="HS256",
        headers={"kid": "id-key"},
    )
    with pytest.raises(ProviderError):
        signed.verifier.verify_pair(symmetric, second, "web", "synthetic-nonce")


def test_oidc_004_unknown_kid_is_throttled_and_rotation_refreshes(signed: SignedProvider) -> None:
    first, second = signed.pair()
    signed.verifier.verify_pair(first, second, "web", "synthetic-nonce")
    claims = jwt.decode(first, options={"verify_signature": False})
    rotated = jwt.encode(
        claims,
        signed.id_key,
        algorithm="RS256",
        headers={"kid": "rotated-key", "jku": "https://attacker.invalid/keys"},
    )
    with pytest.raises(ProviderError):
        signed.verifier.verify_pair(rotated, second, "web", "synthetic-nonce")
    assert len(signed.requests) == 1
    signed.document["keys"][0]["kid"] = "rotated-key"
    signed.verifier._fetched_at -= 31
    signed.verifier.verify_pair(rotated, second, "web", "synthetic-nonce")
    assert len(signed.requests) == 2
    assert all(request.url.host == "issuer.example.test" for request in signed.requests)


def test_oidc_005_signing_keys_and_token_sizes_are_bounded(signed: SignedProvider) -> None:
    first, second = signed.pair()
    signed.document["keys"] *= 6
    with pytest.raises(ProviderError) as error:
        signed.verifier.verify_pair(first, second, "web", "synthetic-nonce")
    assert error.value.status == 503
    with pytest.raises(ProviderError) as error:
        signed.verifier.verify_pair("x" * 16385, second, "web", "synthetic-nonce")
    assert error.value.status == 401


def test_oidc_006_insecure_provider_urls_cannot_enter_production(signed: SignedProvider) -> None:
    config = signed.verifier.config.model_copy(update={"issuer": "http://127.0.0.1:8900/pool"})
    with pytest.raises(ValueError):
        CognitoVerifier(config, signed.verifier.client)
    CognitoVerifier(config, signed.verifier.client, allow_http_loopback=True)
    for value in (
        "https://user:password@issuer.example.test/pool",
        "https://issuer.example.test/pool?",
        "https://issuer.example.test/pool#",
    ):
        with pytest.raises(ValueError):
            CognitoVerifier(config.model_copy(update={"issuer": value}), signed.verifier.client)
