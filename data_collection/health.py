"""
Health check utilities for data sources
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .interfaces.data_source import DataSource

logger = logging.getLogger(__name__)


class DataSourceHealth:
    """Monitor data source health"""
    
    def __init__(self, source: DataSource):
        """
        Initialize health monitor
        
        Args:
            source: Data source to monitor
        """
        self.source = source
        self.last_success: Optional[datetime] = None
        self.last_check: Optional[datetime] = None
        self.consecutive_failures = 0
        self.total_checks = 0
        self.total_failures = 0
    
    def check_health(self) -> bool:
        """
        Perform health check on data source
        
        Returns:
            True if healthy, False otherwise
        """
        self.total_checks += 1
        self.last_check = datetime.now()
        
        try:
            # Check connection status
            if not self.source.is_connected():
                raise Exception("Data source not connected")
            
            # Try to get available symbols as a basic test
            symbols = self.source.get_available_symbols()
            if not symbols:
                raise Exception("No symbols available from data source")
            
            # Try to get available timeframes
            timeframes = self.source.get_available_timeframes()
            if not timeframes:
                raise Exception("No timeframes available from data source")
            
            # Health check passed
            self.last_success = datetime.now()
            self.consecutive_failures = 0
            logger.debug(f"Health check passed for {self.source.name}")
            return True
            
        except Exception as e:
            self.consecutive_failures += 1
            self.total_failures += 1
            logger.warning(
                f"Health check failed for {self.source.name}: {e} "
                f"(consecutive failures: {self.consecutive_failures})"
            )
            return False
    
    def is_healthy(self, max_consecutive_failures: int = 3, max_age_hours: int = 1) -> bool:
        """
        Determine if data source is healthy based on recent checks
        
        Args:
            max_consecutive_failures: Maximum allowed consecutive failures
            max_age_hours: Maximum hours since last successful check
            
        Returns:
            True if healthy, False otherwise
        """
        # Too many consecutive failures
        if self.consecutive_failures > max_consecutive_failures:
            return False
        
        # No successful check yet
        if self.last_success is None:
            return False
        
        # Last successful check too old
        age = datetime.now() - self.last_success
        if age > timedelta(hours=max_age_hours):
            return False
        
        return True
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get detailed health status
        
        Returns:
            Dictionary with health status information
        """
        return {
            'source_name': self.source.name,
            'connected': self.source.is_connected(),
            'healthy': self.is_healthy(),
            'last_success': self.last_success.isoformat() if self.last_success else None,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'consecutive_failures': self.consecutive_failures,
            'total_checks': self.total_checks,
            'total_failures': self.total_failures,
            'success_rate': (
                (self.total_checks - self.total_failures) / self.total_checks * 100
                if self.total_checks > 0 else 0
            )
        }
    
    def reset_stats(self) -> None:
        """Reset health statistics"""
        self.consecutive_failures = 0
        self.total_checks = 0
        self.total_failures = 0
        logger.info(f"Health statistics reset for {self.source.name}")


class HealthMonitor:
    """Monitor health of multiple data sources"""
    
    def __init__(self):
        self.monitors: Dict[str, DataSourceHealth] = {}
    
    def add_source(self, name: str, source: DataSource) -> None:
        """
        Add data source to monitor
        
        Args:
            name: Source name
            source: Data source instance
        """
        self.monitors[name] = DataSourceHealth(source)
        logger.info(f"Added {name} to health monitoring")
    
    def check_all(self) -> Dict[str, bool]:
        """
        Check health of all monitored sources
        
        Returns:
            Dictionary mapping source names to health status
        """
        results = {}
        for name, monitor in self.monitors.items():
            results[name] = monitor.check_health()
        return results
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed status of all monitored sources
        
        Returns:
            Dictionary mapping source names to health status
        """
        return {
            name: monitor.get_health_status()
            for name, monitor in self.monitors.items()
        }
    
    def get_unhealthy_sources(self) -> list:
        """
        Get list of unhealthy sources
        
        Returns:
            List of source names that are unhealthy
        """
        return [
            name for name, monitor in self.monitors.items()
            if not monitor.is_healthy()
        ]
    
    def is_all_healthy(self) -> bool:
        """Check if all sources are healthy"""
        return all(monitor.is_healthy() for monitor in self.monitors.values())

