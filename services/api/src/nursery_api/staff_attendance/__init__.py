"""FEAT-012 staff presence decisions, distinct from child attendance and payroll.

No staff profile, role defaults, correction policy, database or HTTP endpoint is
provided. The future adapter must establish employee status/branch/action access
and lock organization-wide employee presence before committing one open session.
"""

from .presence import decide_staff_attendance

__all__ = ["decide_staff_attendance"]
