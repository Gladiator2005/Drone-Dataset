"""
Utility functions for web scraping.
"""
import time
import random
import hashlib
from urllib import robotparser
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for requests."""
    
    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """
        Initialize rate limiter.
        
        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
    
    def wait(self):
        """Wait before next request."""
        elapsed = time.time() - self.last_request_time
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if elapsed < delay:
            sleep_time = delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


class RobotsTxtChecker:
    """Check robots.txt compliance."""
    
    def __init__(self):
        """Initialize robots.txt checker."""
        self.parsers = {}
    
    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            user_agent: User agent string
            
        Returns:
            True if fetching is allowed, False otherwise
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            if robots_url not in self.parsers:
                rp = robotparser.RobotFileParser()
                rp.set_url(robots_url)
                try:
                    rp.read()
                    self.parsers[robots_url] = rp
                except Exception as e:
                    logger.warning(f"Could not read robots.txt from {robots_url}: {e}")
                    # If we can't read robots.txt, allow by default
                    return True
            
            return self.parsers[robots_url].can_fetch(user_agent, url)
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            return True  # Allow by default on error


def generate_job_id(title: str, company: str, url: str) -> str:
    """
    Generate unique job ID.
    
    Args:
        title: Job title
        company: Company name
        url: Job URL
        
    Returns:
        Unique job ID
    """
    content = f"{title}|{company}|{url}".lower()
    return hashlib.md5(content.encode()).hexdigest()


def normalize_skill(skill: str) -> str:
    """
    Normalize skill name.
    
    Args:
        skill: Raw skill string
        
    Returns:
        Normalized skill name
    """
    # Common normalizations
    skill = skill.lower().strip()
    
    # Mapping of common variations
    mappings = {
        'ml': 'machine learning',
        'dl': 'deep learning',
        'cv': 'computer vision',
        'nlp': 'natural language processing',
        'sklearn': 'scikit-learn',
        'tf': 'tensorflow',
        'py': 'python',
        'js': 'javascript',
    }
    
    return mappings.get(skill, skill)


def clean_text(text: Optional[str]) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()
