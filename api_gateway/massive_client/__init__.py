"""
Massive API Gateway Client

Thin wrapper around polygon-api-client with resilience features.
"""

from .master_client import MassiveClient
from .rest import MassiveRest

__all__ = ['MassiveClient', 'MassiveRest']

