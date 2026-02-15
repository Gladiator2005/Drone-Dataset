"""
SQLite storage for job discovery system.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path
import logging
from ..models import Job
from ..utils import get_config

logger = logging.getLogger(__name__)


class JobStorage:
    """SQLite storage for jobs."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            config = get_config()
            db_name = config.get('storage.database', 'job_discovery.db')
            db_path = Path(__file__).parent.parent / db_name
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                company_category TEXT,
                locations TEXT,
                remote_type TEXT,
                job_type TEXT,
                duration TEXT,
                is_paid INTEGER,
                stipend_salary TEXT,
                experience_level TEXT,
                required_skills TEXT,
                preferred_skills TEXT,
                domain TEXT,
                description TEXT,
                posting_date TEXT,
                deadline TEXT,
                url TEXT,
                source TEXT,
                relevance_score REAL,
                skill_match_score REAL,
                fetched_at TEXT,
                is_new INTEGER DEFAULT 1,
                seen_count INTEGER DEFAULT 1,
                last_seen TEXT
            )
        ''')
        
        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relevance ON jobs(relevance_score DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_company ON jobs(company)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON jobs(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fetched_at ON jobs(fetched_at)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_job(self, job: Job):
        """
        Save or update a job.
        
        Args:
            job: Job to save
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if job exists
        cursor.execute('SELECT job_id, seen_count FROM jobs WHERE job_id = ?', (job.job_id,))
        existing = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if existing:
            # Update existing job
            seen_count = existing[1] + 1
            cursor.execute('''
                UPDATE jobs SET
                    title = ?, company = ?, company_category = ?, locations = ?,
                    remote_type = ?, job_type = ?, duration = ?, is_paid = ?,
                    stipend_salary = ?, experience_level = ?, required_skills = ?,
                    preferred_skills = ?, domain = ?, description = ?,
                    posting_date = ?, deadline = ?, url = ?, source = ?,
                    relevance_score = ?, skill_match_score = ?, fetched_at = ?,
                    is_new = 0, seen_count = ?, last_seen = ?
                WHERE job_id = ?
            ''', (
                job.title, job.company,
                job.company_category.value if job.company_category else None,
                json.dumps(job.locations),
                job.remote_type.value if job.remote_type else None,
                job.job_type.value if job.job_type else None,
                job.duration, job.is_paid, job.stipend_salary, job.experience_level,
                json.dumps(job.required_skills), json.dumps(job.preferred_skills),
                job.domain, job.description,
                job.posting_date.isoformat() if job.posting_date else None,
                job.deadline.isoformat() if job.deadline else None,
                job.url, job.source, job.relevance_score, job.skill_match_score,
                job.fetched_at.isoformat(), seen_count, now, job.job_id
            ))
        else:
            # Insert new job
            cursor.execute('''
                INSERT INTO jobs (
                    job_id, title, company, company_category, locations,
                    remote_type, job_type, duration, is_paid, stipend_salary,
                    experience_level, required_skills, preferred_skills, domain,
                    description, posting_date, deadline, url, source,
                    relevance_score, skill_match_score, fetched_at, is_new,
                    seen_count, last_seen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.job_id, job.title, job.company,
                job.company_category.value if job.company_category else None,
                json.dumps(job.locations),
                job.remote_type.value if job.remote_type else None,
                job.job_type.value if job.job_type else None,
                job.duration, job.is_paid, job.stipend_salary, job.experience_level,
                json.dumps(job.required_skills), json.dumps(job.preferred_skills),
                job.domain, job.description,
                job.posting_date.isoformat() if job.posting_date else None,
                job.deadline.isoformat() if job.deadline else None,
                job.url, job.source, job.relevance_score, job.skill_match_score,
                job.fetched_at.isoformat(), 1, 1, now
            ))
        
        conn.commit()
        conn.close()
    
    def save_jobs(self, jobs: List[Job]):
        """
        Save multiple jobs.
        
        Args:
            jobs: List of jobs to save
        """
        for job in jobs:
            self.save_job(job)
        
        logger.info(f"Saved {len(jobs)} jobs to database")
    
    def get_new_jobs(self, limit: int = 100) -> List[Job]:
        """
        Get new jobs since last run.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of new jobs
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM jobs
            WHERE is_new = 1
            ORDER BY relevance_score DESC
            LIMIT ?
        ''', (limit,))
        
        jobs = [self._row_to_job(row) for row in cursor.fetchall()]
        
        conn.close()
        return jobs
    
    def get_top_jobs(self, limit: int = 50, min_score: float = 70) -> List[Job]:
        """
        Get top-ranked jobs.
        
        Args:
            limit: Maximum number of jobs to return
            min_score: Minimum relevance score
            
        Returns:
            List of top jobs
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM jobs
            WHERE relevance_score >= ?
            ORDER BY relevance_score DESC
            LIMIT ?
        ''', (min_score, limit))
        
        jobs = [self._row_to_job(row) for row in cursor.fetchall()]
        
        conn.close()
        return jobs
    
    def mark_jobs_as_seen(self):
        """Mark all new jobs as seen."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE jobs SET is_new = 0 WHERE is_new = 1')
        
        conn.commit()
        conn.close()
    
    def cleanup_old_jobs(self, days: int = 90):
        """
        Remove jobs older than specified days.
        
        Args:
            days: Number of days to keep
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM jobs WHERE fetched_at < ?', (cutoff,))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted} old jobs")
    
    def get_stats(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total jobs
        cursor.execute('SELECT COUNT(*) FROM jobs')
        stats['total_jobs'] = cursor.fetchone()[0]
        
        # New jobs
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE is_new = 1')
        stats['new_jobs'] = cursor.fetchone()[0]
        
        # Jobs by source
        cursor.execute('SELECT source, COUNT(*) FROM jobs GROUP BY source')
        stats['by_source'] = dict(cursor.fetchall())
        
        # Average relevance score
        cursor.execute('SELECT AVG(relevance_score) FROM jobs')
        stats['avg_relevance'] = cursor.fetchone()[0] or 0
        
        conn.close()
        return stats
    
    def _row_to_job(self, row) -> Job:
        """Convert database row to Job object."""
        from ..models import RemoteType, CompanyCategory, JobType
        
        return Job(
            job_id=row[0],
            title=row[1],
            company=row[2],
            company_category=CompanyCategory(row[3]) if row[3] else None,
            locations=json.loads(row[4]) if row[4] else [],
            remote_type=RemoteType(row[5]) if row[5] else None,
            job_type=JobType(row[6]) if row[6] else None,
            duration=row[7],
            is_paid=bool(row[8]) if row[8] is not None else None,
            stipend_salary=row[9],
            experience_level=row[10],
            required_skills=json.loads(row[11]) if row[11] else [],
            preferred_skills=json.loads(row[12]) if row[12] else [],
            domain=row[13],
            description=row[14],
            posting_date=datetime.fromisoformat(row[15]) if row[15] else None,
            deadline=datetime.fromisoformat(row[16]) if row[16] else None,
            url=row[17],
            source=row[18],
            relevance_score=row[19] or 0.0,
            skill_match_score=row[20] or 0.0,
            fetched_at=datetime.fromisoformat(row[21]) if row[21] else datetime.now()
        )
