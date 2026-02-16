"""
Main job discovery engine.
"""
from typing import List
import logging
from .models import Job, UserProfile
from .scrapers import RemoteOKScraper, IntershalaScraper, CompanyScraper
from .intelligence import SkillExtractor
from .scoring import RelevanceScorer
from .filters import JobPipeline
from .storage import JobStorage
from .alerts import AlertManager
from .utils import get_config

logger = logging.getLogger(__name__)


class JobDiscoveryEngine:
    """Main job discovery engine."""
    
    def __init__(self, user_profile: UserProfile = None):
        """
        Initialize discovery engine.
        
        Args:
            user_profile: User profile for matching (loads from config if None)
        """
        self.config = get_config()
        
        # Load or use provided user profile
        if user_profile is None:
            user_profile = self._load_user_profile()
        self.user_profile = user_profile
        
        # Initialize components
        self.skill_extractor = SkillExtractor()
        self.scorer = RelevanceScorer(user_profile)
        self.pipeline = JobPipeline()
        self.storage = JobStorage()
        self.alerts = AlertManager()
        
        # Initialize scrapers
        self.scrapers = []
        self._init_scrapers()
    
    def _load_user_profile(self) -> UserProfile:
        """Load user profile from config."""
        # Get all skills from config
        skills = []
        
        # Languages
        user_langs = self.config.get('user.skills.languages', [])
        skills.extend(user_langs)
        
        # Frameworks
        user_frameworks = self.config.get('user.skills.frameworks', [])
        skills.extend(user_frameworks)
        
        # Domains
        user_domains = self.config.get('user.skills.domains', [])
        skills.extend(user_domains)
        
        # Tools
        user_tools = self.config.get('user.skills.tools', [])
        skills.extend(user_tools)
        
        # Create profile
        profile = UserProfile(
            city=self.config.get('user.city', 'Bangalore'),
            country=self.config.get('user.country', 'India'),
            location_radius_km=self.config.get('user.location_radius_km', 50),
            skills=skills,
            target_roles=self.config.get('user.target_roles', [])
        )
        
        return profile
    
    def _init_scrapers(self):
        """Initialize all scrapers based on config."""
        # RemoteOK scraper
        remote_ok = self.config.get('sources.remote_platforms', [])
        for platform in remote_ok:
            if platform.get('name') == 'RemoteOK' and platform.get('enabled', True):
                self.scrapers.append(RemoteOKScraper())
        
        # Add more scrapers as needed
        # Note: Other scrapers would be initialized here when implemented
        
        logger.info(f"Initialized {len(self.scrapers)} scrapers")
    
    def discover(self) -> List[Job]:
        """
        Run discovery process across all sources.
        
        Returns:
            List of discovered and processed jobs
        """
        logger.info("Starting job discovery...")
        
        all_jobs = []
        
        # Scrape from all sources
        for scraper in self.scrapers:
            try:
                logger.info(f"Scraping from {scraper.get_name()}...")
                jobs = scraper.scrape()
                
                # Extract skills from job descriptions
                for job in jobs:
                    if job.description and not job.required_skills:
                        extracted = self.skill_extractor.extract_skills(
                            job.title + " " + job.description
                        )
                        job.required_skills = extracted
                
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs from {scraper.get_name()}")
            except Exception as e:
                logger.error(f"Error scraping {scraper.get_name()}: {e}")
        
        logger.info(f"Scraped {len(all_jobs)} total jobs")
        
        # Score jobs
        logger.info("Scoring jobs...")
        self.scorer.score_jobs(all_jobs)
        
        # Filter and deduplicate
        logger.info("Filtering and deduplicating...")
        processed_jobs = self.pipeline.process(all_jobs)
        
        # Save to storage
        logger.info("Saving to database...")
        self.storage.save_jobs(processed_jobs)
        
        logger.info(f"Discovery complete: {len(processed_jobs)} jobs after processing")
        
        return processed_jobs
    
    def get_new_jobs(self) -> List[Job]:
        """
        Get new jobs since last run.
        
        Returns:
            List of new jobs
        """
        return self.storage.get_new_jobs()
    
    def get_top_jobs(self, limit: int = 50) -> List[Job]:
        """
        Get top-ranked jobs.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of top jobs
        """
        return self.storage.get_top_jobs(limit)
    
    def send_alerts(self, jobs: List[Job] = None):
        """
        Send alerts for jobs.
        
        Args:
            jobs: List of jobs to alert about (gets new jobs if None)
        """
        if jobs is None:
            jobs = self.get_new_jobs()
        
        self.alerts.send_alerts(jobs)
    
    def run_discovery_cycle(self):
        """Run complete discovery cycle with alerts."""
        jobs = self.discover()
        new_jobs = self.get_new_jobs()
        
        if new_jobs:
            self.send_alerts(new_jobs)
        
        self.storage.mark_jobs_as_seen()
    
    def get_stats(self) -> dict:
        """
        Get discovery statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.storage.get_stats()
