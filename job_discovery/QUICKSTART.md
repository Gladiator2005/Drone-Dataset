# Quick Start Guide

**🔗 Repository:** [https://github.com/Gladiator2005/Drone-Dataset](https://github.com/Gladiator2005/Drone-Dataset)

Get started with the Job Discovery System in 5 minutes!

## 1. Installation

```bash
cd job_discovery
pip install -r requirements.txt
```

## 2. Run the Demo

See the system in action with sample data:

```bash
cd /path/to/Drone-Dataset
PYTHONPATH=$(pwd):$PYTHONPATH python job_discovery/demo.py
```

This will:
- Create sample AI/ML job postings
- Extract and match skills
- Score jobs based on relevance
- Filter and deduplicate
- Save to database
- Show top opportunities
- Send alerts

## 3. Configure Your Profile

Edit `job_discovery/config.yaml`:

```yaml
user:
  city: "Your City"
  skills:
    languages: [Python, SQL]
    frameworks: [TensorFlow, PyTorch, Pandas, NumPy]
    domains: [Computer Vision, NLP, Machine Learning]
    tools: [Git, Docker, Linux]
```

Or use the CLI:

```bash
cd /path/to/Drone-Dataset
PYTHONPATH=$(pwd):$PYTHONPATH python -m job_discovery configure --city "Bangalore"
```

## 4. Search for Jobs

Run a one-time search:

```bash
cd /path/to/Drone-Dataset
PYTHONPATH=$(pwd):$PYTHONPATH python -m job_discovery search
```

Note: This requires internet access to scrape real job boards. In restricted environments, use the demo script instead.

## 5. View Results

```bash
cd /path/to/Drone-Dataset
PYTHONPATH=$(pwd):$PYTHONPATH python -m job_discovery results
```

View only new jobs:

```bash
PYTHONPATH=$(pwd):$PYTHONPATH python -m job_discovery results --new
```

Export to JSON:

```bash
PYTHONPATH=$(pwd):$PYTHONPATH python -m job_discovery results --format json --output my_jobs.json
```

## 6. Check Statistics

```bash
cd /path/to/Drone-Dataset
PYTHONPATH=$(pwd):$PYTHONPATH python -m job_discovery stats
```

## 7. Automated Discovery (Optional)

Run scheduled discovery (checks for new jobs every 6 hours):

```bash
cd /path/to/Drone-Dataset
PYTHONPATH=$(pwd):$PYTHONPATH python -m job_discovery run
```

Press Ctrl+C to stop.

## Using as a Python Library

```python
import sys
sys.path.insert(0, '/path/to/Drone-Dataset')

from job_discovery.engine import JobDiscoveryEngine
from job_discovery.models import UserProfile

# Create custom profile
profile = UserProfile(
    city="Mumbai",
    skills=["Python", "TensorFlow", "PyTorch", "NumPy"],
    target_roles=["ML Intern", "AI Intern"]
)

# Create engine
engine = JobDiscoveryEngine(user_profile=profile)

# Discover jobs
jobs = engine.discover()

# Get top jobs
top_jobs = engine.get_top_jobs(limit=10)

for job in top_jobs:
    print(f"{job.title} at {job.company} - Score: {job.relevance_score:.1f}")
```

See `job_discovery/examples.py` for more examples.

## Troubleshooting

### "No module named 'job_discovery'"

Set PYTHONPATH:
```bash
cd /path/to/Drone-Dataset
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### No jobs found

The system needs internet access to scrape job boards. If you're in a restricted environment:
1. Run the demo: `python job_discovery/demo.py`
2. Or implement offline scrapers for local data

### Rate limiting errors

Edit `config.yaml` and increase delays:
```yaml
scraping:
  rate_limit:
    min_delay: 5
    max_delay: 10
```

## Next Steps

- **Add More Scrapers**: Implement scrapers for specific job boards you're interested in
- **Customize Scoring**: Adjust weights in `config.yaml` to match your preferences
- **Setup Email Alerts**: Configure SMTP settings in `config.yaml`
- **Track Applications**: Use the database to track which jobs you've applied to

## Getting Help

- Check the full README: `job_discovery/README.md`
- Run demo: `python job_discovery/demo.py`
- Run examples: `python job_discovery/examples.py`
- View help: `python -m job_discovery --help`

Happy job hunting! 🎯
