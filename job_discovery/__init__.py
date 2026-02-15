"""
Job Discovery System

A personal/hobby AIML internship and entry-level job discovery system.
"""

__version__ = '1.0.0'
__author__ = 'Job Discovery Team'

from .engine import JobDiscoveryEngine
from .models import Job, UserProfile
from .utils import get_config

__all__ = ['JobDiscoveryEngine', 'Job', 'UserProfile', 'get_config']
