"""
Job discovery scheduler.
"""
import schedule
import time
from typing import List, Callable
import logging
from ..utils import get_config

logger = logging.getLogger(__name__)


class DiscoveryScheduler:
    """Schedule job discovery runs."""
    
    def __init__(self):
        """Initialize scheduler."""
        self.config = get_config()
        self.jobs = []
        self.running = False
    
    def add_job(self, func: Callable, interval_hours: int, name: str = None):
        """
        Add a scheduled job.
        
        Args:
            func: Function to call
            interval_hours: Interval in hours
            name: Job name for logging
        """
        job_name = name or func.__name__
        
        if interval_hours < 1:
            logger.warning(f"Interval too small for {job_name}, setting to 1 hour")
            interval_hours = 1
        
        # Schedule the job
        schedule.every(interval_hours).hours.do(func)
        
        self.jobs.append({
            'name': job_name,
            'interval_hours': interval_hours,
            'function': func
        })
        
        logger.info(f"Scheduled '{job_name}' to run every {interval_hours} hours")
    
    def run_once(self, func: Callable):
        """
        Run a function once immediately.
        
        Args:
            func: Function to call
        """
        try:
            logger.info(f"Running {func.__name__} once")
            func()
        except Exception as e:
            logger.error(f"Error running {func.__name__}: {e}")
    
    def start(self):
        """Start the scheduler loop."""
        if not self.jobs:
            logger.warning("No jobs scheduled")
            return
        
        self.running = True
        logger.info(f"Starting scheduler with {len(self.jobs)} jobs")
        
        # Run all jobs once at startup
        logger.info("Running initial discovery sweep...")
        for job in self.jobs:
            try:
                job['function']()
            except Exception as e:
                logger.error(f"Error in initial run of {job['name']}: {e}")
        
        # Start scheduling loop
        logger.info("Starting scheduling loop...")
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                self.stop()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        schedule.clear()
        logger.info("Scheduler stopped")
    
    def get_status(self) -> List[dict]:
        """
        Get status of scheduled jobs.
        
        Returns:
            List of job status dictionaries
        """
        return self.jobs.copy()
