"""
Base scraper class for job discovery.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from abc import ABC, abstractmethod
import logging
from ..models import Job
from ..utils import RateLimiter, RobotsTxtChecker, get_config

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all job scrapers."""
    
    def __init__(self, name: str):
        """
        Initialize scraper.
        
        Args:
            name: Scraper name
        """
        self.name = name
        self.config = get_config()
        
        # Initialize rate limiter
        min_delay = self.config.get('scraping.rate_limit.min_delay', 2)
        max_delay = self.config.get('scraping.rate_limit.max_delay', 5)
        self.rate_limiter = RateLimiter(min_delay, max_delay)
        
        # Initialize robots.txt checker
        self.robots_checker = RobotsTxtChecker()
        
        # User agent
        self.user_agent = self.config.get(
            'scraping.user_agent',
            'Mozilla/5.0 (compatible; JobDiscoveryBot/1.0)'
        )
        
        self.timeout = self.config.get('scraping.timeout_seconds', 30)
        self.respect_robots = self.config.get('scraping.respect_robots_txt', True)
    
    def _can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL can be fetched
        """
        if not self.respect_robots:
            return True
        
        return self.robots_checker.can_fetch(url, self.user_agent)
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make HTTP request with rate limiting and error handling.
        
        Args:
            url: URL to fetch
            method: HTTP method
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object or None on error
        """
        # Check robots.txt
        if not self._can_fetch(url):
            logger.warning(f"Blocked by robots.txt: {url}")
            return None
        
        # Rate limit
        self.rate_limiter.wait()
        
        # Set headers
        headers = kwargs.get('headers', {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.user_agent
        kwargs['headers'] = headers
        
        # Set timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        try:
            logger.info(f"Fetching {url}")
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content.
        
        Args:
            html: HTML string
            
        Returns:
            BeautifulSoup object or None
        """
        try:
            return BeautifulSoup(html, 'lxml')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return None
    
    @abstractmethod
    def scrape(self) -> List[Job]:
        """
        Scrape jobs from source.
        
        Returns:
            List of Job objects
        """
        pass
    
    def get_name(self) -> str:
        """Get scraper name."""
        return self.name
