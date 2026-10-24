"""FEAT-030 stage/history and appointment decisions without persistence or routes.

The application adapter must resolve authoritative branch access and approved
workflow policy, then persist a decision and its history/audit in one versioned
transaction. This package neither authenticates users nor creates enrollments.
Appointment availability and reason codes remain explicit trusted inputs;
calendar completeness and concurrent host locking belong to the future adapter.
"""

from .appointments import decide_appointment
from .stages import decide_stage_change

__all__ = ["decide_appointment", "decide_stage_change"]
