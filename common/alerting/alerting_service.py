"""
Error alerting and escalation system
"""

import logging
from typing import Dict, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CriticalError(Exception):
    """Critical error that requires immediate attention"""
    pass


class AlertingService:
    """Service for escalating critical errors"""
    
    def __init__(self):
        self.alerts = []
        self.alert_handlers = []
    
    def register_handler(self, handler):
        """Register an alert handler"""
        self.alert_handlers.append(handler)
    
    def escalate_error(
        self, 
        error: Exception, 
        context: Dict[str, Any], 
        severity: AlertSeverity = AlertSeverity.CRITICAL
    ) -> None:
        """
        Escalate error to alerting system
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
            severity: Severity level
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity.value,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        # Log the alert
        if severity == AlertSeverity.CRITICAL:
            logger.critical(f"CRITICAL ALERT: {error}", extra=context)
        elif severity == AlertSeverity.HIGH:
            logger.error(f"HIGH SEVERITY ALERT: {error}", extra=context)
        elif severity == AlertSeverity.MEDIUM:
            logger.warning(f"MEDIUM SEVERITY ALERT: {error}", extra=context)
        else:
            logger.info(f"LOW SEVERITY ALERT: {error}", extra=context)
        
        # Store alert
        self.alerts.append(alert)
        
        # Call registered handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def get_recent_alerts(self, limit: int = 10) -> list:
        """Get recent alerts"""
        return self.alerts[-limit:]
    
    def clear_alerts(self) -> None:
        """Clear all alerts"""
        self.alerts.clear()


# Global alerting service instance
alerting_service = AlertingService()


def escalate_critical_error(error: Exception, context: Dict[str, Any]) -> None:
    """
    Escalate critical error to alerting system
    
    Args:
        error: Exception that occurred
        context: Additional context about the error
    """
    alerting_service.escalate_error(error, context, AlertSeverity.CRITICAL)


def escalate_error(error: Exception, context: Dict[str, Any], severity: AlertSeverity = AlertSeverity.MEDIUM) -> None:
    """
    Escalate error to alerting system
    
    Args:
        error: Exception that occurred
        context: Additional context about the error
        severity: Severity level
    """
    alerting_service.escalate_error(error, context, severity)

