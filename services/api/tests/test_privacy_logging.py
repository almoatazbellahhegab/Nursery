"""Access logs must not persist authorization codes, nonce/state or search text."""

import logging

from nursery_api.runtime.privacy_logging import PrivateAccessFilter


def test_private_access_log_removes_every_query_value() -> None:
    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        "synthetic",
        1,
        '%s - "%s %s HTTP/%s" %d',
        (
            "127.0.0.1",
            "GET",
            "/api/v1/auth/oidc/callback?code=synthetic-code&state=synthetic-state",
            "1.1",
            303,
        ),
        None,
    )
    assert PrivateAccessFilter().filter(record)
    message = record.getMessage()
    assert "[redacted]" in message
    assert "synthetic-code" not in message and "synthetic-state" not in message


def test_private_access_log_preserves_status_and_plain_path() -> None:
    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        "synthetic",
        1,
        '%s - "%s %s HTTP/%s" %d',
        ("127.0.0.1", "GET", "/api/v1/health", "1.1", 200),
        None,
    )
    assert PrivateAccessFilter().filter(record)
    assert "/api/v1/health HTTP/1.1" in record.getMessage()
