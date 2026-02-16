#!/usr/bin/env python3
"""
Demo script to show job discovery system capabilities.
This creates sample data to demonstrate the system without requiring internet access.
"""
from datetime import datetime, timedelta
from job_discovery.models import Job, UserProfile, RemoteType, CompanyCategory, JobType
from job_discovery.intelligence import SkillExtractor, SkillMatcher
from job_discovery.scoring import RelevanceScorer
from job_discovery.filters import JobPipeline
from job_discovery.storage import JobStorage
from job_discovery.alerts import AlertManager
from job_discovery.utils import generate_job_id

def create_sample_jobs():
    """Create sample job postings for demo."""
    jobs = []
    
    # Job 1: Remote ML Internship
    jobs.append(Job(
        job_id=generate_job_id("Machine Learning Intern", "TechCorp AI", "https://example.com/1"),
        title="Machine Learning Intern",
        company="TechCorp AI",
        company_category=CompanyCategory.STARTUP,
        locations=["Remote"],
        remote_type=RemoteType.FULLY_REMOTE,
        job_type=JobType.INTERNSHIP,
        duration="3-6 months",
        is_paid=True,
        stipend_salary="₹25,000 - ₹35,000/month",
        experience_level="Student/Fresher",
        required_skills=["Python", "TensorFlow", "Machine Learning", "NumPy", "Pandas"],
        preferred_skills=["PyTorch", "Computer Vision"],
        domain="Machine Learning",
        description="Seeking ML intern to work on deep learning models for computer vision applications. "
                   "Will work with TensorFlow and PyTorch on real-world datasets.",
        posting_date=datetime.now() - timedelta(days=2),
        url="https://example.com/jobs/ml-intern-1",
        source="Demo"
    ))
    
    # Job 2: NLP Research Intern
    jobs.append(Job(
        job_id=generate_job_id("NLP Research Intern", "AI Research Labs", "https://example.com/2"),
        title="NLP Research Intern",
        company="AI Research Labs",
        company_category=CompanyCategory.RESEARCH,
        locations=["Bangalore", "Remote"],
        remote_type=RemoteType.HYBRID,
        job_type=JobType.INTERNSHIP,
        duration="6 months",
        is_paid=True,
        stipend_salary="₹30,000/month",
        experience_level="Student",
        required_skills=["Python", "NLP", "Natural Language Processing", "PyTorch", "Transformers"],
        preferred_skills=["LLMs", "Hugging Face", "BERT"],
        domain="NLP",
        description="Work on cutting-edge NLP research including large language models and transformers. "
                   "Experience with Hugging Face and transformer architectures preferred.",
        posting_date=datetime.now() - timedelta(days=1),
        url="https://example.com/jobs/nlp-intern-2",
        source="Demo"
    ))
    
    # Job 3: Data Science Intern
    jobs.append(Job(
        job_id=generate_job_id("Data Science Intern", "DataCo", "https://example.com/3"),
        title="Data Science Intern",
        company="DataCo",
        company_category=CompanyCategory.MNC,
        locations=["Mumbai", "Pune"],
        remote_type=RemoteType.ONSITE,
        job_type=JobType.INTERNSHIP,
        duration="3 months",
        is_paid=True,
        stipend_salary="₹20,000/month",
        experience_level="Fresher",
        required_skills=["Python", "Pandas", "NumPy", "SQL", "Data Science"],
        preferred_skills=["Machine Learning", "Scikit-learn"],
        domain="Data Science",
        description="Join our data science team to analyze customer data and build predictive models. "
                   "Strong Python and SQL skills required.",
        posting_date=datetime.now() - timedelta(days=5),
        url="https://example.com/jobs/ds-intern-3",
        source="Demo"
    ))
    
    # Job 4: Computer Vision Intern
    jobs.append(Job(
        job_id=generate_job_id("Computer Vision Intern", "VisionTech", "https://example.com/4"),
        title="Computer Vision Intern",
        company="VisionTech",
        company_category=CompanyCategory.STARTUP,
        locations=["Remote"],
        remote_type=RemoteType.FULLY_REMOTE,
        job_type=JobType.INTERNSHIP,
        duration="4-6 months",
        is_paid=True,
        stipend_salary="₹28,000/month",
        experience_level="Student",
        required_skills=["Python", "Computer Vision", "OpenCV", "Deep Learning", "PyTorch"],
        preferred_skills=["YOLO", "Object Detection", "TensorFlow"],
        domain="Computer Vision",
        description="Build and deploy computer vision models for object detection and image segmentation. "
                   "Experience with OpenCV and PyTorch required.",
        posting_date=datetime.now() - timedelta(days=3),
        url="https://example.com/jobs/cv-intern-4",
        source="Demo"
    ))
    
    # Job 5: Junior ML Engineer (Entry Level)
    jobs.append(Job(
        job_id=generate_job_id("Junior ML Engineer", "ML Solutions", "https://example.com/5"),
        title="Junior ML Engineer",
        company="ML Solutions",
        company_category=CompanyCategory.REMOTE_FIRST,
        locations=["Remote - India"],
        remote_type=RemoteType.INDIA_REMOTE,
        job_type=JobType.ENTRY_LEVEL,
        is_paid=True,
        stipend_salary="₹5-7 LPA",
        experience_level="0-1 years",
        required_skills=["Python", "Machine Learning", "TensorFlow", "Git", "Linux"],
        preferred_skills=["Docker", "AWS", "MLOps"],
        domain="Machine Learning",
        description="Join our remote team as a junior ML engineer. Work on deploying ML models to production. "
                   "Fresh graduates with strong ML fundamentals welcome.",
        posting_date=datetime.now() - timedelta(days=4),
        url="https://example.com/jobs/jr-ml-5",
        source="Demo"
    ))
    
    return jobs


def demo_discovery_system():
    """Demonstrate the job discovery system."""
    print("=" * 80)
    print("JOB DISCOVERY SYSTEM DEMO")
    print("=" * 80)
    print()
    
    # Create sample user profile
    print("📋 User Profile:")
    user_profile = UserProfile(
        city="Bangalore",
        country="India",
        location_radius_km=50,
        skills=[
            "Python", "TensorFlow", "PyTorch", "NumPy", "Pandas",
            "Computer Vision", "NLP", "Machine Learning", "Git", "Linux"
        ],
        target_roles=["ML Intern", "AI Intern", "Data Science Intern"]
    )
    print(f"   Location: {user_profile.city}, {user_profile.country}")
    print(f"   Skills: {', '.join(user_profile.skills[:5])} and {len(user_profile.skills)-5} more")
    print()
    
    # Create sample jobs
    print("🔍 Creating sample job postings...")
    jobs = create_sample_jobs()
    print(f"   Created {len(jobs)} sample jobs")
    print()
    
    # Extract skills
    print("🧠 Extracting skills from job descriptions...")
    extractor = SkillExtractor()
    for job in jobs:
        if not job.required_skills:
            extracted = extractor.extract_skills(job.title + " " + job.description)
            job.required_skills = extracted
    print(f"   Skills extracted for all jobs")
    print()
    
    # Score jobs
    print("⭐ Scoring jobs based on relevance...")
    scorer = RelevanceScorer(user_profile)
    scored_jobs = scorer.score_jobs(jobs)
    print(f"   Scored {len(scored_jobs)} jobs")
    print()
    
    # Filter and process
    print("🔧 Filtering and deduplicating...")
    pipeline = JobPipeline()
    processed_jobs = pipeline.process(scored_jobs)
    print(f"   {len(processed_jobs)} jobs after filtering")
    print()
    
    # Save to database
    print("💾 Saving to database...")
    storage = JobStorage()
    storage.save_jobs(processed_jobs)
    stats = storage.get_stats()
    print(f"   Database now has {stats['total_jobs']} total jobs")
    print()
    
    # Display top jobs
    print("🎯 TOP OPPORTUNITIES:")
    print("-" * 80)
    for i, job in enumerate(processed_jobs[:3], 1):
        print(f"\n{i}. {job.title} at {job.company}")
        print(f"   📍 {job.remote_type.value if job.remote_type else 'Location TBD'}")
        print(f"   💰 {job.stipend_salary if job.stipend_salary else 'Salary not disclosed'}")
        print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")
        print(f"   🎯 Skill Match: {job.skill_match_score:.1f}/100")
        print(f"   📚 Skills: {', '.join(job.required_skills[:5])}")
        if len(job.required_skills) > 5:
            print(f"              and {len(job.required_skills)-5} more...")
        print(f"   🔗 {job.url}")
    
    print()
    print("-" * 80)
    
    # Send alerts
    print("\n🔔 Sending alerts for high-relevance jobs...")
    alerts = AlertManager()
    high_relevance = [j for j in processed_jobs if j.relevance_score >= 75]
    if high_relevance:
        alerts.send_alerts(high_relevance)
    else:
        print(f"   No jobs with relevance ≥ 75")
    
    print()
    print("=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
    print()
    print("💡 Try these commands:")
    print("   python -m job_discovery results    # View stored results")
    print("   python -m job_discovery stats      # View statistics")
    print("   python -m job_discovery configure  # Update your profile")
    print()


if __name__ == "__main__":
    demo_discovery_system()
