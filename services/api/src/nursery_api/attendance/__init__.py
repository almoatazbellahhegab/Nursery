"""FEAT-011 domain decisions; no transport, database or authorization provider.

Public entry point: decide_attendance. Only an application adapter that resolves
the child and authoritative access grant may call it. The adapter must commit
state, idempotency receipt, audit and outbox atomically under a version lock.
This package does not authorize HTTP requests or provide durable deduplication.
"""

from .decisions import decide_attendance

__all__ = ["decide_attendance"]
