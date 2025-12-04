"""
Error alerting and escalation system
"""

from .alerting_service import (
    AlertingService,
    AlertSeverity,
    CriticalError,
    alerting_service,
    escalate_error,
    escalate_critical_error,
)

__all__ = [
    "AlertingService",
    "AlertSeverity",
    "CriticalError",
    "alerting_service",
    "escalate_error",
    "escalate_critical_error",
]
