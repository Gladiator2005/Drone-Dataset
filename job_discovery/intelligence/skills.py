"""
Skill intelligence and matching system.
"""
import re
from typing import List, Set, Dict
from ..utils import normalize_skill, get_config
import logging

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Extract skills from job descriptions."""
    
    def __init__(self):
        """Initialize skill extractor."""
        self.config = get_config()
        
        # Load taxonomy from config
        self.languages = set(
            skill.lower() for skill in self.config.get('taxonomy.languages', [])
        )
        self.frameworks = set(
            skill.lower() for skill in self.config.get('taxonomy.frameworks', [])
        )
        self.domains = set(
            skill.lower() for skill in self.config.get('taxonomy.domains', [])
        )
        self.tools = set(
            skill.lower() for skill in self.config.get('taxonomy.tools', [])
        )
        
        # Combine all skills
        self.all_skills = self.languages | self.frameworks | self.domains | self.tools
        
        # Create pattern for skill matching
        self._build_patterns()
    
    def _build_patterns(self):
        """Build regex patterns for skill matching."""
        # Sort by length (longest first) to match compound terms first
        skills_sorted = sorted(self.all_skills, key=len, reverse=True)
        
        # Escape special regex characters and create pattern
        escaped_skills = [re.escape(skill) for skill in skills_sorted]
        self.pattern = re.compile(
            r'\b(' + '|'.join(escaped_skills) + r')\b',
            re.IGNORECASE
        )
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text.
        
        Args:
            text: Text to extract skills from (job description, title, etc.)
            
        Returns:
            List of extracted skills
        """
        if not text:
            return []
        
        text = text.lower()
        
        # Find all matches
        matches = self.pattern.findall(text)
        
        # Normalize and deduplicate
        skills = list(set(normalize_skill(skill) for skill in matches))
        
        return skills
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize skills into taxonomy categories.
        
        Args:
            skills: List of skills
            
        Returns:
            Dictionary with categorized skills
        """
        categorized = {
            'languages': [],
            'frameworks': [],
            'domains': [],
            'tools': []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            
            if skill_lower in self.languages:
                categorized['languages'].append(skill)
            if skill_lower in self.frameworks:
                categorized['frameworks'].append(skill)
            if skill_lower in self.domains:
                categorized['domains'].append(skill)
            if skill_lower in self.tools:
                categorized['tools'].append(skill)
        
        return categorized


class SkillMatcher:
    """Match user skills with job requirements."""
    
    def __init__(self, user_skills: List[str]):
        """
        Initialize skill matcher.
        
        Args:
            user_skills: List of user's skills
        """
        self.user_skills = set(normalize_skill(skill) for skill in user_skills)
    
    def calculate_match_score(self, job_skills: List[str], 
                             preferred_skills: List[str] = None) -> float:
        """
        Calculate skill match score using Jaccard similarity.
        
        Args:
            job_skills: Required skills for the job
            preferred_skills: Preferred skills for the job
            
        Returns:
            Match score between 0 and 1
        """
        if not job_skills and not preferred_skills:
            return 0.0
        
        # Normalize job skills
        required = set(normalize_skill(skill) for skill in job_skills)
        preferred = set(normalize_skill(skill) for skill in (preferred_skills or []))
        
        # Calculate match for required skills (80% weight)
        if required:
            required_match = len(self.user_skills & required) / len(required)
        else:
            required_match = 0.0
        
        # Calculate match for preferred skills (20% weight)
        if preferred:
            preferred_match = len(self.user_skills & preferred) / len(preferred)
        else:
            preferred_match = 0.0
        
        # Weighted score
        if required and preferred:
            score = 0.8 * required_match + 0.2 * preferred_match
        elif required:
            score = required_match
        else:
            score = preferred_match
        
        return score
    
    def get_matched_skills(self, job_skills: List[str]) -> List[str]:
        """
        Get list of skills that match between user and job.
        
        Args:
            job_skills: Job's required skills
            
        Returns:
            List of matched skills
        """
        job_skills_norm = set(normalize_skill(skill) for skill in job_skills)
        matched = self.user_skills & job_skills_norm
        return list(matched)
    
    def get_missing_skills(self, job_skills: List[str]) -> List[str]:
        """
        Get list of skills required by job that user doesn't have.
        
        Args:
            job_skills: Job's required skills
            
        Returns:
            List of missing skills
        """
        job_skills_norm = set(normalize_skill(skill) for skill in job_skills)
        missing = job_skills_norm - self.user_skills
        return list(missing)
