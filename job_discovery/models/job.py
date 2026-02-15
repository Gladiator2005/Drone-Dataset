"""
Data models for job discovery system.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class RemoteType(str, Enum):
    """Type of remote work arrangement."""
    FULLY_REMOTE = "Fully Remote"
    INDIA_REMOTE = "India-Only Remote"
    HYBRID = "Hybrid"
    ONSITE = "On-site"


class CompanyCategory(str, Enum):
    """Category of company."""
    STARTUP = "Startup"
    MNC = "MNC"
    RESEARCH = "Research"
    REMOTE_FIRST = "Remote-First"


class JobType(str, Enum):
    """Type of position."""
    INTERNSHIP = "Internship"
    ENTRY_LEVEL = "Entry Level"
    JUNIOR = "Junior"


@dataclass
class Job:
    """
    Represents a job or internship opportunity.
    """
    # Basic Information
    job_id: str
    title: str
    company: str
    company_category: Optional[CompanyCategory] = None
    
    # Location
    locations: List[str] = field(default_factory=list)
    remote_type: Optional[RemoteType] = None
    
    # Job Details
    job_type: Optional[JobType] = None
    duration: Optional[str] = None  # For internships
    is_paid: Optional[bool] = None
    stipend_salary: Optional[str] = None
    experience_level: Optional[str] = None
    
    # Skills
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    domain: Optional[str] = None
    
    # Description
    description: str = ""
    
    # Dates
    posting_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Source
    url: str = ""
    source: str = ""
    
    # Computed Fields
    relevance_score: float = 0.0
    skill_match_score: float = 0.0
    
    # Metadata
    fetched_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return {
            'job_id': self.job_id,
            'title': self.title,
            'company': self.company,
            'company_category': self.company_category.value if self.company_category else None,
            'locations': self.locations,
            'remote_type': self.remote_type.value if self.remote_type else None,
            'job_type': self.job_type.value if self.job_type else None,
            'duration': self.duration,
            'is_paid': self.is_paid,
            'stipend_salary': self.stipend_salary,
            'experience_level': self.experience_level,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills,
            'domain': self.domain,
            'description': self.description,
            'posting_date': self.posting_date.isoformat() if self.posting_date else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'url': self.url,
            'source': self.source,
            'relevance_score': self.relevance_score,
            'skill_match_score': self.skill_match_score,
            'fetched_at': self.fetched_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Job':
        """Create Job from dictionary."""
        # Convert string enums back to enum objects
        if data.get('company_category'):
            data['company_category'] = CompanyCategory(data['company_category'])
        if data.get('remote_type'):
            data['remote_type'] = RemoteType(data['remote_type'])
        if data.get('job_type'):
            data['job_type'] = JobType(data['job_type'])
        
        # Convert ISO format strings back to datetime
        if data.get('posting_date'):
            data['posting_date'] = datetime.fromisoformat(data['posting_date'])
        if data.get('deadline'):
            data['deadline'] = datetime.fromisoformat(data['deadline'])
        if data.get('fetched_at'):
            data['fetched_at'] = datetime.fromisoformat(data['fetched_at'])
        
        return cls(**data)


@dataclass
class UserProfile:
    """
    User profile for matching jobs.
    """
    city: str
    country: str = "India"
    location_radius_km: int = 50
    
    skills: List[str] = field(default_factory=list)
    target_roles: List[str] = field(default_factory=list)
    
    min_stipend: Optional[int] = None
    only_paid: bool = False
    max_experience_years: int = 2
    
    def get_skill_vector(self) -> set:
        """Get normalized skill set."""
        return {skill.lower().strip() for skill in self.skills}
