"""
Job filtering and deduplication.
"""
from typing import List, Set
from difflib import SequenceMatcher
import logging
from ..models import Job, JobType, RemoteType
from ..utils import get_config

logger = logging.getLogger(__name__)


class JobFilter:
    """Filter jobs based on criteria."""
    
    def __init__(self):
        """Initialize job filter."""
        self.config = get_config()
        self.min_relevance = self.config.get('scoring.min_relevance_score', 70)
        self.only_internships_or_remote = self.config.get(
            'filtering.only_internships_or_remote', True
        )
    
    def filter_jobs(self, jobs: List[Job]) -> List[Job]:
        """
        Filter jobs based on criteria.
        
        Args:
            jobs: List of jobs to filter
            
        Returns:
            Filtered list of jobs
        """
        filtered = []
        
        for job in jobs:
            if self._should_include(job):
                filtered.append(job)
        
        logger.info(f"Filtered {len(jobs)} jobs to {len(filtered)} jobs")
        return filtered
    
    def _should_include(self, job: Job) -> bool:
        """
        Check if job should be included.
        
        Args:
            job: Job to check
            
        Returns:
            True if job should be included
        """
        # Check relevance score
        if job.relevance_score < self.min_relevance:
            return False
        
        # If filtering for internships or remote only
        if self.only_internships_or_remote:
            is_internship = job.job_type == JobType.INTERNSHIP
            is_remote = job.remote_type in [
                RemoteType.FULLY_REMOTE,
                RemoteType.INDIA_REMOTE
            ]
            
            if not (is_internship or is_remote):
                return False
        
        return True


class JobDeduplicator:
    """Deduplicate jobs across sources."""
    
    def __init__(self, fuzzy_threshold: float = 0.85):
        """
        Initialize deduplicator.
        
        Args:
            fuzzy_threshold: Similarity threshold for fuzzy matching (0-1)
        """
        self.fuzzy_threshold = fuzzy_threshold
    
    def deduplicate(self, jobs: List[Job]) -> List[Job]:
        """
        Remove duplicate jobs.
        
        Args:
            jobs: List of jobs to deduplicate
            
        Returns:
            Deduplicated list of jobs
        """
        if not jobs:
            return []
        
        # First pass: exact duplicates by job_id
        seen_ids = set()
        unique_jobs = []
        
        for job in jobs:
            if job.job_id not in seen_ids:
                seen_ids.add(job.job_id)
                unique_jobs.append(job)
        
        # Second pass: fuzzy matching by title and company
        deduplicated = []
        seen_signatures = []
        
        for job in unique_jobs:
            if not self._is_duplicate(job, seen_signatures):
                deduplicated.append(job)
                seen_signatures.append((job.title.lower(), job.company.lower()))
        
        logger.info(f"Deduplicated {len(jobs)} jobs to {len(deduplicated)} unique jobs")
        return deduplicated
    
    def _is_duplicate(self, job: Job, seen_signatures: List[tuple]) -> bool:
        """
        Check if job is duplicate of any seen job.
        
        Args:
            job: Job to check
            seen_signatures: List of (title, company) tuples
            
        Returns:
            True if job is duplicate
        """
        job_title = job.title.lower()
        job_company = job.company.lower()
        
        for seen_title, seen_company in seen_signatures:
            # Check company match (must be exact)
            if job_company == seen_company:
                # Check title similarity
                similarity = self._calculate_similarity(job_title, seen_title)
                if similarity >= self.fuzzy_threshold:
                    logger.debug(f"Duplicate found: '{job.title}' at {job.company} "
                               f"(similarity: {similarity:.2f})")
                    return True
        
        return False
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score (0-1)
        """
        return SequenceMatcher(None, str1, str2).ratio()


class JobPipeline:
    """Complete job processing pipeline."""
    
    def __init__(self):
        """Initialize pipeline."""
        self.filter = JobFilter()
        self.deduplicator = JobDeduplicator()
    
    def process(self, jobs: List[Job]) -> List[Job]:
        """
        Process jobs through complete pipeline.
        
        Args:
            jobs: List of jobs to process
            
        Returns:
            Processed and filtered jobs
        """
        logger.info(f"Processing {len(jobs)} jobs through pipeline")
        
        # Filter jobs
        filtered = self.filter.filter_jobs(jobs)
        
        # Deduplicate
        deduplicated = self.deduplicator.deduplicate(filtered)
        
        # Sort by relevance score (highest first)
        sorted_jobs = sorted(deduplicated, key=lambda j: j.relevance_score, reverse=True)
        
        logger.info(f"Pipeline complete: {len(sorted_jobs)} jobs after filtering and deduplication")
        return sorted_jobs
