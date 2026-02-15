#!/usr/bin/env python3
"""
Example: Using the Job Discovery System Programmatically

This script shows how to use the job discovery system as a library
in your own Python code.
"""
import sys
sys.path.insert(0, '/home/runner/work/Drone-Dataset/Drone-Dataset')

from job_discovery.models import UserProfile
from job_discovery.engine import JobDiscoveryEngine
from job_discovery.storage import JobStorage


def example_basic_usage():
    """Example 1: Basic usage - discover and view jobs."""
    print("Example 1: Basic Job Discovery\n")
    
    # Create engine with default config
    engine = JobDiscoveryEngine()
    
    # Run discovery (would scrape from real sources with internet)
    print("Running discovery...")
    jobs = engine.discover()
    print(f"Found {len(jobs)} jobs\n")
    
    # Get top jobs
    top_jobs = engine.get_top_jobs(limit=5)
    
    print("Top 5 opportunities:")
    for i, job in enumerate(top_jobs, 1):
        print(f"{i}. {job.title} at {job.company} (Score: {job.relevance_score:.1f})")


def example_custom_profile():
    """Example 2: Using a custom user profile."""
    print("\nExample 2: Custom User Profile\n")
    
    # Create custom profile
    profile = UserProfile(
        city="Mumbai",
        skills=[
            "Python", "R", "SQL", "Pandas", "NumPy",
            "Scikit-learn", "Data Science", "Statistics"
        ],
        target_roles=["Data Science Intern", "Data Analyst Intern"],
        only_paid=True
    )
    
    # Create engine with custom profile
    engine = JobDiscoveryEngine(user_profile=profile)
    
    print(f"Profile: {profile.city}, {len(profile.skills)} skills")
    print(f"Target roles: {', '.join(profile.target_roles[:2])}")


def example_database_operations():
    """Example 3: Working with the database."""
    print("\nExample 3: Database Operations\n")
    
    storage = JobStorage()
    
    # Get statistics
    stats = storage.get_stats()
    print(f"Database stats:")
    print(f"  Total jobs: {stats['total_jobs']}")
    print(f"  New jobs: {stats['new_jobs']}")
    print(f"  Average relevance: {stats['avg_relevance']:.1f}")
    
    if stats.get('by_source'):
        print(f"  Jobs by source:")
        for source, count in stats['by_source'].items():
            print(f"    - {source}: {count}")


def example_export_data():
    """Example 4: Exporting job data."""
    print("\nExample 4: Exporting Data\n")
    
    storage = JobStorage()
    jobs = storage.get_top_jobs(limit=10)
    
    if jobs:
        # Export to JSON
        import json
        data = [job.to_dict() for job in jobs]
        
        print(f"Exporting {len(jobs)} jobs to JSON...")
        with open('/tmp/my_jobs.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("✓ Exported to /tmp/my_jobs.json")
    else:
        print("No jobs to export")


def example_skill_matching():
    """Example 5: Skill matching and analysis."""
    print("\nExample 5: Skill Matching\n")
    
    from job_discovery.intelligence import SkillMatcher
    
    user_skills = ["Python", "TensorFlow", "PyTorch", "NumPy", "Pandas"]
    job_skills = ["Python", "TensorFlow", "Machine Learning", "Deep Learning"]
    
    matcher = SkillMatcher(user_skills)
    
    score = matcher.calculate_match_score(job_skills)
    matched = matcher.get_matched_skills(job_skills)
    missing = matcher.get_missing_skills(job_skills)
    
    print(f"User skills: {', '.join(user_skills)}")
    print(f"Job requirements: {', '.join(job_skills)}")
    print(f"\nMatch score: {score*100:.1f}%")
    print(f"Matched skills: {', '.join(matched)}")
    print(f"Missing skills: {', '.join(missing)}")


def main():
    """Run all examples."""
    print("="*80)
    print("JOB DISCOVERY SYSTEM - PROGRAMMATIC USAGE EXAMPLES")
    print("="*80)
    
    try:
        example_basic_usage()
        example_custom_profile()
        example_database_operations()
        example_export_data()
        example_skill_matching()
        
        print("\n" + "="*80)
        print("All examples completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
