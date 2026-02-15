# Drone Dataset Repository

This repository contains datasets and projects related to AI/ML development.

## Contents

### 1. Job Discovery System (`job_discovery/`)

A comprehensive AIML internship and entry-level job discovery system built with Python.

**Features:**
- 🔍 Multi-source job scraping (RemoteOK, Internshala, company pages, etc.)
- 🧠 Intelligent skill extraction and matching
- ⭐ Multi-factor relevance scoring
- 🎯 Smart filtering and deduplication
- 💾 SQLite storage with history tracking
- 🔔 Console and email alerts
- ⏰ Automated scheduling
- 📊 Rich CLI interface with export capabilities

**Quick Start:**
```bash
cd job_discovery
pip install -r requirements.txt
python demo.py
```

**Documentation:**
- [README](job_discovery/README.md) - Complete documentation
- [QUICKSTART](job_discovery/QUICKSTART.md) - 5-minute guide
- [ARCHITECTURE](job_discovery/ARCHITECTURE.md) - System design
- [IMPLEMENTATION_SUMMARY](job_discovery/IMPLEMENTATION_SUMMARY.md) - Complete overview

**Usage:**
```bash
# Search for jobs
python -m job_discovery search

# View results
python -m job_discovery results

# View statistics
python -m job_discovery stats

# Export to JSON
python -m job_discovery results --format json --output jobs.json
```

See the [full documentation](job_discovery/README.md) for detailed usage instructions.

### 2. Drone Dataset (`split_dataset.zip`)

Dataset for drone-related computer vision and machine learning applications.

---

## Project Status

- ✅ **Job Discovery System**: Complete and functional (v1.0.0)
- 📦 **Drone Dataset**: Available for download

## Requirements

**Job Discovery System:**
- Python 3.9+
- See [requirements.txt](job_discovery/requirements.txt) for dependencies

## Contributing

This is primarily a personal/educational repository, but contributions are welcome!

## License

This repository is for educational and personal use.

## Contact

For questions or issues, please open an issue on GitHub.

---

**Happy Learning and Job Hunting! 🎯**
