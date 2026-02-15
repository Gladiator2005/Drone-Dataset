"""
Scrapers package for job discovery system.
"""
from .base import BaseScraper
from .remoteok import RemoteOKScraper
from .internshala import IntershalaScraper
from .company import CompanyScraper

__all__ = [
    'BaseScraper',
    'RemoteOKScraper',
    'IntershalaScraper',
    'CompanyScraper'
]
