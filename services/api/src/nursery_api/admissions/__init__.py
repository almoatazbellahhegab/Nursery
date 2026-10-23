"""FEAT-030 stage/history decisions with no PII, persistence or public routes.

The application adapter must resolve authoritative branch access and approved
workflow policy, then persist a decision and its history/audit in one versioned
transaction. This package neither authenticates users nor creates enrollments.
"""

from .stages import decide_stage_change

__all__ = ["decide_stage_change"]
