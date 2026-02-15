"""
Job relevance scoring system.
"""
from datetime import datetime, timedelta
from typing import List
import logging
from ..models import Job, UserProfile, JobType, RemoteType
from ..intelligence import SkillMatcher
from ..utils import get_config

logger = logging.getLogger(__name__)


class RelevanceScorer:
    """Calculate relevance scores for jobs."""
    
    def __init__(self, user_profile: UserProfile):
        """
        Initialize relevance scorer.
        
        Args:
            user_profile: User profile for scoring
        """
        self.user_profile = user_profile
        self.config = get_config()
        
        # Load weights from config
        weights = self.config.get('scoring.weights', {})
        self.skill_weight = weights.get('skill_match', 0.40)
        self.internship_weight = weights.get('internship_fit', 0.20)
        self.location_weight = weights.get('location_match', 0.15)
        self.freshness_weight = weights.get('freshness', 0.15)
        self.company_weight = weights.get('company_relevance', 0.10)
        
        # Initialize skill matcher
        self.skill_matcher = SkillMatcher(user_profile.skills)
    
    def score_job(self, job: Job) -> float:
        """
        Calculate relevance score for a job.
        
        Args:
            job: Job to score
            
        Returns:
            Relevance score (0-100)
        """
        scores = {
            'skill': self._score_skill_match(job),
            'internship': self._score_internship_fit(job),
            'location': self._score_location_match(job),
            'freshness': self._score_freshness(job),
            'company': self._score_company_relevance(job)
        }
        
        # Calculate weighted score
        total_score = (
            scores['skill'] * self.skill_weight +
            scores['internship'] * self.internship_weight +
            scores['location'] * self.location_weight +
            scores['freshness'] * self.freshness_weight +
            scores['company'] * self.company_weight
        )
        
        # Scale to 0-100
        final_score = total_score * 100
        
        logger.debug(f"Job '{job.title}' at {job.company}: {final_score:.1f} "
                    f"(skill={scores['skill']:.2f}, intern={scores['internship']:.2f}, "
                    f"loc={scores['location']:.2f}, fresh={scores['freshness']:.2f}, "
                    f"company={scores['company']:.2f})")
        
        return final_score
    
    def _score_skill_match(self, job: Job) -> float:
        """Score based on skill match (0-1)."""
        if not job.required_skills and not job.preferred_skills:
            return 0.5  # Neutral score if no skills listed
        
        score = self.skill_matcher.calculate_match_score(
            job.required_skills,
            job.preferred_skills
        )
        
        # Store skill match score in job
        job.skill_match_score = score * 100
        
        return score
    
    def _score_internship_fit(self, job: Job) -> float:
        """Score based on internship/student fit (0-1)."""
        score = 0.0
        
        # Check if it's an internship
        if job.job_type == JobType.INTERNSHIP:
            score = 1.0
        elif job.job_type == JobType.ENTRY_LEVEL:
            score = 0.8
        else:
            # Check title for intern-related keywords
            title_lower = job.title.lower()
            if 'intern' in title_lower:
                score = 1.0
            elif any(word in title_lower for word in ['junior', 'graduate', 'entry', 'trainee']):
                score = 0.7
            else:
                score = 0.3
        
        return score
    
    def _score_location_match(self, job: Job) -> float:
        """Score based on location match (0-1)."""
        score = 0.0
        
        # Remote jobs get high score
        if job.remote_type in [RemoteType.FULLY_REMOTE, RemoteType.INDIA_REMOTE]:
            score = 1.0
        elif job.remote_type == RemoteType.HYBRID:
            score = 0.7
        
        # Check if job location matches user location
        if job.locations:
            user_city = self.user_profile.city.lower()
            for location in job.locations:
                if user_city in location.lower():
                    score = max(score, 1.0)
                    break
                # Check for India
                elif 'india' in location.lower() and job.remote_type == RemoteType.INDIA_REMOTE:
                    score = max(score, 0.9)
        
        return score
    
    def _score_freshness(self, job: Job) -> float:
        """Score based on posting freshness (0-1)."""
        if not job.posting_date:
            return 0.5  # Neutral score if date unknown
        
        days_old = (datetime.now() - job.posting_date).days
        
        # Score decreases with age
        if days_old <= 3:
            return 1.0
        elif days_old <= 7:
            return 0.9
        elif days_old <= 14:
            return 0.7
        elif days_old <= 30:
            return 0.5
        elif days_old <= 60:
            return 0.3
        else:
            return 0.1
    
    def _score_company_relevance(self, job: Job) -> float:
        """Score based on company relevance to AI/ML (0-1)."""
        score = 0.5  # Default neutral score
        
        # Check company category
        from ..models import CompanyCategory
        if job.company_category == CompanyCategory.RESEARCH:
            score = 1.0
        elif job.company_category == CompanyCategory.STARTUP:
            score = 0.8
        elif job.company_category == CompanyCategory.REMOTE_FIRST:
            score = 0.9
        
        # Check if job domain is AI/ML related
        if job.domain:
            domain_lower = job.domain.lower()
            if any(term in domain_lower for term in ['ai', 'ml', 'machine learning', 'deep learning']):
                score = max(score, 0.9)
        
        return score
    
    def score_jobs(self, jobs: List[Job]) -> List[Job]:
        """
        Score multiple jobs and update their relevance scores.
        
        Args:
            jobs: List of jobs to score
            
        Returns:
            List of jobs with updated scores
        """
        for job in jobs:
            job.relevance_score = self.score_job(job)
        
        return jobs
