"""
RemoteOK scraper - uses public JSON API.
"""
from typing import List, Optional
from datetime import datetime
import logging
from .base import BaseScraper
from ..models import Job, RemoteType, CompanyCategory, JobType
from ..utils import generate_job_id, clean_text

logger = logging.getLogger(__name__)


class RemoteOKScraper(BaseScraper):
    """Scraper for RemoteOK public API."""
    
    def __init__(self):
        """Initialize RemoteOK scraper."""
        super().__init__("RemoteOK")
        self.api_url = "https://remoteok.com/api"
    
    def scrape(self) -> List[Job]:
        """
        Scrape jobs from RemoteOK API.
        
        Returns:
            List of Job objects
        """
        jobs = []
        
        try:
            response = self._make_request(self.api_url)
            if not response:
                return jobs
            
            data = response.json()
            
            # First item is metadata, skip it
            if isinstance(data, list) and len(data) > 0:
                data = data[1:]
            
            for job_data in data:
                job = self._parse_job(job_data)
                if job:
                    jobs.append(job)
            
            logger.info(f"Scraped {len(jobs)} jobs from RemoteOK")
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")
        
        return jobs
    
    def _parse_job(self, data: dict) -> Optional[Job]:
        """
        Parse job from RemoteOK API response.
        
        Args:
            data: Job data dictionary
            
        Returns:
            Job object or None
        """
        try:
            # Extract basic info
            title = clean_text(data.get('position', ''))
            company = clean_text(data.get('company', ''))
            url = data.get('url', '')
            
            if not title or not company:
                return None
            
            # Check if it's ML/AI related
            description = clean_text(data.get('description', ''))
            tags = [tag.lower() for tag in data.get('tags', [])]
            
            # Filter for AI/ML roles
            ai_keywords = [
                'machine learning', 'ml', 'ai', 'artificial intelligence',
                'data science', 'deep learning', 'computer vision', 'nlp',
                'natural language', 'python', 'tensorflow', 'pytorch'
            ]
            
            is_ai_role = any(keyword in title.lower() for keyword in ai_keywords)
            is_ai_role = is_ai_role or any(keyword in ' '.join(tags) for keyword in ai_keywords)
            
            if not is_ai_role:
                return None
            
            # Check if it's intern/entry level
            is_intern = 'intern' in title.lower() or 'intern' in tags
            is_entry = any(word in title.lower() for word in ['junior', 'entry', 'graduate', 'associate'])
            
            # Determine job type
            job_type = None
            if is_intern:
                job_type = JobType.INTERNSHIP
            elif is_entry:
                job_type = JobType.ENTRY_LEVEL
            
            # Extract skills from tags
            skills = [clean_text(tag) for tag in data.get('tags', []) if tag]
            
            # Generate job ID
            job_id = generate_job_id(title, company, url)
            
            # Create Job object
            job = Job(
                job_id=job_id,
                title=title,
                company=company,
                company_category=CompanyCategory.REMOTE_FIRST,
                locations=["Remote"],
                remote_type=RemoteType.FULLY_REMOTE,
                job_type=job_type,
                description=description,
                required_skills=skills,
                url=url if url.startswith('http') else f"https://remoteok.com{url}",
                source=self.name,
                posting_date=self._parse_date(data.get('date'))
            )
            
            # Check if India-eligible
            location_str = data.get('location', '').lower()
            if 'worldwide' in location_str or 'anywhere' in location_str or not location_str:
                job.remote_type = RemoteType.FULLY_REMOTE
            
            return job
            
        except Exception as e:
            logger.error(f"Error parsing RemoteOK job: {e}")
            return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date from RemoteOK format."""
        if not date_str:
            return None
        
        try:
            # RemoteOK uses Unix timestamps
            timestamp = int(date_str)
            return datetime.fromtimestamp(timestamp)
        except:
            return None
