# Job Discovery System

**🔗 Main Repository:** [https://github.com/Gladiator2005/Drone-Dataset](https://github.com/Gladiator2005/Drone-Dataset)

A personal/hobby AIML internship and entry-level job discovery system built with Python. This system automatically scrapes, filters, scores, and alerts you about relevant AI/ML opportunities across multiple platforms.

## 🎯 Overview

This is a learning project designed to help B.Tech students and early-career professionals in AI/ML find relevant internships and entry-level positions. It combines web scraping, skill matching, and intelligent filtering to surface the best opportunities.

### Key Features

- 🔍 **Multi-Source Scraping**: Scrapes jobs from multiple platforms (RemoteOK, Internshala, company career pages, etc.)
- 🧠 **Skill Intelligence**: Extracts and matches skills using an AI/ML taxonomy
- ⭐ **Smart Scoring**: Ranks opportunities based on skill match, location, freshness, and more
- 🎯 **Relevance Filtering**: Only shows jobs that meet your criteria
- 🔔 **Alerting**: Console and email alerts for new opportunities
- 📊 **Analytics**: Track discovery statistics and trends
- 🗄️ **SQLite Storage**: Persistent storage with deduplication
- ⏰ **Scheduling**: Automated discovery runs at configurable intervals

## 🚀 Quick Start

### Installation

1. Navigate to the job_discovery directory:
```bash
cd job_discovery
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Edit `config.yaml` to set your profile:

```yaml
user:
  city: "Your City"
  skills:
    languages:
      - Python
    frameworks:
      - TensorFlow
      - PyTorch
    domains:
      - Computer Vision
      - NLP
```

### Basic Usage

**Run a one-time search:**
```bash
python -m job_discovery search
```

**Start scheduled discovery:**
```bash
python -m job_discovery run
```

**View results:**
```bash
python -m job_discovery results
```

**Configure your profile:**
```bash
python -m job_discovery configure --city "Bangalore" --skills "Python,TensorFlow,PyTorch"
```

**View statistics:**
```bash
python -m job_discovery stats
```

## 📁 Project Structure

```
job_discovery/
├── __init__.py           # Package initialization
├── __main__.py          # Entry point for CLI
├── config.yaml          # Configuration file
├── requirements.txt     # Python dependencies
├── cli.py              # Command-line interface
├── engine.py           # Main discovery engine
│
├── models/             # Data models
│   ├── __init__.py
│   └── job.py         # Job and UserProfile models
│
├── scrapers/          # Web scrapers
│   ├── __init__.py
│   ├── base.py       # Base scraper class
│   ├── remoteok.py   # RemoteOK scraper (working)
│   ├── internshala.py # Internshala scraper (template)
│   └── company.py    # Generic company scraper
│
├── intelligence/      # Skill extraction and matching
│   ├── __init__.py
│   └── skills.py
│
├── scoring/          # Relevance scoring
│   ├── __init__.py
│   └── relevance.py
│
├── filters/          # Filtering and deduplication
│   ├── __init__.py
│   └── pipeline.py
│
├── storage/          # Database storage
│   ├── __init__.py
│   └── database.py
│
├── alerts/           # Alert system
│   ├── __init__.py
│   └── manager.py
│
├── scheduler/        # Job scheduling
│   ├── __init__.py
│   └── runner.py
│
└── utils/            # Utility functions
    ├── __init__.py
    ├── config.py     # Configuration management
    └── scraping.py   # Scraping utilities
```

## 🔧 Architecture

### 1. Scraping Layer
- **Base Scraper**: Abstract class with rate limiting, robots.txt checking, and error handling
- **Specific Scrapers**: Implementations for each source (RemoteOK, Internshala, etc.)
- **Ethical Scraping**: Respects robots.txt, uses rate limiting, proper user agents

### 2. Data Models
- **Job**: Complete job/internship information with skills, location, type, etc.
- **UserProfile**: Your skills, location, and preferences for matching

### 3. Intelligence Layer
- **SkillExtractor**: Extracts skills from job descriptions using taxonomy
- **SkillMatcher**: Matches user skills with job requirements (Jaccard similarity)

### 4. Scoring System
Multi-factor relevance scoring:
- Skill match (40%)
- Internship/student fit (20%)
- Location match (15%)
- Posting freshness (15%)
- Company relevance (10%)

### 5. Filtering Pipeline
- Relevance threshold (≥70 by default)
- Internship or remote-eligible only
- Deduplication across sources

### 6. Storage
- SQLite database for persistent storage
- Tracks new vs. seen jobs
- Maintains history and statistics

### 7. Alerting
- Console alerts with rich formatting
- Optional email alerts via SMTP
- Triggered by relevance score and job type

### 8. Scheduling
- Configurable intervals per source
- High-activity sources: 3-4 hours
- Low-activity sources: 12-24 hours

## 📊 Output Formats

### Console (Rich Tables)
Beautiful, color-coded tables showing:
- 🌍 Remote Internships
- 📍 Nearby Opportunities
- Relevance scores, skills, and direct apply links

### JSON Export
```bash
python -m job_discovery results --format json --output jobs.json
```

### CSV Export
```bash
python -m job_discovery results --format csv --output jobs.csv
```

## ⚙️ Configuration

Key configuration options in `config.yaml`:

```yaml
# User Profile
user:
  city: "Bangalore"
  location_radius_km: 50
  skills: [...]
  target_roles: [...]

# Scraping
scraping:
  rate_limit:
    min_delay: 2
    max_delay: 5
  respect_robots_txt: true

# Scoring
scoring:
  weights:
    skill_match: 0.40
    internship_fit: 0.20
    location_match: 0.15
    freshness: 0.15
    company_relevance: 0.10
  min_relevance_score: 70

# Alerts
alerts:
  console_enabled: true
  email_enabled: false
  triggers:
    min_relevance_score: 75
```

## 🌐 Supported Sources

### Currently Implemented
- ✅ **RemoteOK**: Public JSON API, fully functional

### Template/Mock Implementations
- 🔄 **Internshala**: Template ready for implementation
- 🔄 **Naukri**: Template ready
- 🔄 **Indeed India**: Template ready
- 🔄 **Company Career Pages**: Generic scraper template

### Adding New Scrapers

1. Create a new scraper class inheriting from `BaseScraper`
2. Implement the `scrape()` method
3. Parse HTML/JSON and return `Job` objects
4. Add to `engine.py` initialization

Example:
```python
from .scrapers.base import BaseScraper

class MyJobBoardScraper(BaseScraper):
    def __init__(self):
        super().__init__("MyJobBoard")
    
    def scrape(self):
        # Your scraping logic
        return jobs
```

## 🛡️ Ethical Scraping

This system follows ethical scraping practices:

- ✅ Respects `robots.txt`
- ✅ Rate limiting with random delays (2-5s)
- ✅ Proper User-Agent headers
- ✅ Public pages only (no login required)
- ✅ Caching to reduce load
- ✅ Error handling and graceful failures

## 📈 Usage Examples

### Example 1: Daily Internship Discovery
```bash
# Run once to see what's available
python -m job_discovery search

# View results
python -m job_discovery results --new

# Start automated daily runs
python -m job_discovery run
```

### Example 2: Export Top Opportunities
```bash
# Get top 100 opportunities as JSON
python -m job_discovery results --limit 100 --format json --output my_jobs.json
```

### Example 3: Track Statistics
```bash
# Check how many jobs found
python -m job_discovery stats
```

## 🔍 Skill Taxonomy

The system recognizes these categories:

**Languages**: Python, R, SQL, Java, C++, Julia, Scala

**Frameworks**: TensorFlow, PyTorch, Keras, scikit-learn, NumPy, Pandas, OpenCV, Hugging Face, spaCy, NLTK

**Domains**: Computer Vision, NLP, Large Language Models, Machine Learning, Deep Learning, Data Science, Reinforcement Learning, Robotics

**Tools**: Git, Docker, Kubernetes, AWS, Azure, GCP, Linux, Jupyter, MLflow

## 🐛 Troubleshooting

### No jobs found
- Check your `config.yaml` settings
- Try lowering `min_relevance_score`
- Ensure scrapers are enabled in config

### Rate limiting errors
- Increase delays in `config.yaml`
- Check if source is temporarily blocking requests

### Database issues
- Delete `job_discovery.db` to reset
- Check file permissions

## 🚧 Limitations

This is a hobby/learning project with some limitations:

1. **Mock Scrapers**: Most scrapers are templates/mocks. Only RemoteOK is fully functional.
2. **No Authentication**: Can't scrape login-required pages
3. **HTML Changes**: Scrapers may break if websites change their structure
4. **Rate Limits**: May hit rate limits on aggressive scraping
5. **False Positives**: Skill matching is keyword-based, not semantic

## 🎓 Learning Opportunities

This project demonstrates:

- Web scraping with `requests` and `BeautifulSoup`
- Data modeling with Python dataclasses
- SQLite database operations
- CLI development with `argparse` and `rich`
- Scheduling and automation
- Text processing and keyword extraction
- Scoring and ranking algorithms
- Software architecture and modular design

## 📝 Future Enhancements

Potential improvements:

- [ ] Implement all scrapers (Internshala, Naukri, Indeed, etc.)
- [ ] Add semantic skill matching with embeddings
- [ ] Web dashboard with Flask/FastAPI
- [ ] Machine learning for better relevance scoring
- [ ] Resume/CV matching
- [ ] Application tracking
- [ ] Interview preparation suggestions
- [ ] Salary prediction models
- [ ] Company research integration

## 📄 License

This is a personal/educational project. Use responsibly and respect the terms of service of websites you scrape.

## 🤝 Contributing

This is a hobby project, but contributions are welcome! Feel free to:

1. Fork the repository
2. Implement missing scrapers
3. Add new features
4. Fix bugs
5. Improve documentation

## ⚠️ Disclaimer

This tool is for educational and personal use only. Always respect:
- Website terms of service
- robots.txt directives
- Rate limits
- Privacy and data protection laws

The authors are not responsible for misuse of this tool.

## 📧 Contact

For questions or suggestions, please open an issue on the repository.

---

**Happy Job Hunting! 🎯**
