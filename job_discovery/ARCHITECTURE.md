# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Job Discovery System                          │
└─────────────────────────────────────────────────────────────────────┘

         ┌────────────────────────────────────────┐
         │         CLI Interface (cli.py)         │
         │  Commands: search, run, results,       │
         │           configure, stats             │
         └──────────────┬─────────────────────────┘
                        │
         ┌──────────────▼──────────────────────────┐
         │    Discovery Engine (engine.py)         │
         │  Orchestrates the entire pipeline       │
         └──────────────┬──────────────────────────┘
                        │
         ┌──────────────┴──────────────────────────┐
         │                                          │
    ┌────▼─────┐  ┌─────────┐  ┌──────────┐  ┌────▼─────┐
    │ Scrapers │  │ Skills  │  │ Scoring  │  │ Storage  │
    │          │  │ Intel.  │  │          │  │          │
    └──────────┘  └─────────┘  └──────────┘  └──────────┘
```

## Detailed Component Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. SCRAPING LAYER                                                    │
└─────────────────────────────────────────────────────────────────────┘

  Job Boards              Remote Platforms        Company Pages
  ┌──────────┐           ┌──────────┐            ┌──────────┐
  │Internshala│           │RemoteOK  │            │ Google   │
  │ Naukri    │  ──────▶  │Wellfound │  ──────▶   │Microsoft │
  │ Indeed    │           │AngelList │            │ NVIDIA   │
  └──────────┘           └──────────┘            └──────────┘
       │                      │                        │
       └──────────────────────┼────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Base Scraper      │
                    │  - Rate Limiting   │
                    │  - robots.txt      │
                    │  - Error Handling  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Job Objects       │
                    └─────────┬──────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 2. INTELLIGENCE LAYER                                                │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────▼──────────┐
                    │  Skill Extractor   │
                    │  - Keyword Match   │
                    │  - Taxonomy        │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Skill Matcher     │
                    │  - Jaccard Sim.    │
                    │  - Match Score     │
                    └─────────┬──────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 3. SCORING LAYER                                                     │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────▼──────────┐
                    │ Relevance Scorer   │
                    │ ┌────────────────┐ │
                    │ │ Skill: 40%     │ │
                    │ │ Internship: 20%│ │
                    │ │ Location: 15%  │ │
                    │ │ Freshness: 15% │ │
                    │ │ Company: 10%   │ │
                    │ └────────────────┘ │
                    └─────────┬──────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 4. FILTERING LAYER                                                   │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────▼──────────┐
                    │   Job Filter       │
                    │  - Min Score ≥70   │
                    │  - Internship/Rem. │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Deduplicator      │
                    │  - Fuzzy Match     │
                    │  - Title + Company │
                    └─────────┬──────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 5. STORAGE LAYER                                                     │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────▼──────────┐
                    │   SQLite DB        │
                    │  ┌──────────────┐  │
                    │  │ Jobs Table   │  │
                    │  │ - job_id     │  │
                    │  │ - title      │  │
                    │  │ - company    │  │
                    │  │ - skills     │  │
                    │  │ - score      │  │
                    │  │ - is_new     │  │
                    │  └──────────────┘  │
                    └─────────┬──────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 6. ALERT LAYER                                                       │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────▼──────────┐
                    │  Alert Manager     │
                    └───┬──────────┬─────┘
                        │          │
            ┌───────────▼─┐    ┌──▼──────────┐
            │   Console   │    │   Email     │
            │   Alerts    │    │   Alerts    │
            └─────────────┘    └─────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 7. SCHEDULING LAYER                                                  │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  Scheduler          │
                    │  - High freq: 3-4h  │
                    │  - Low freq: 12-24h │
                    │  - Adaptive timing  │
                    └─────────────────────┘
```

## Data Flow

```
┌────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Scrape │────▶│ Extract  │────▶│  Score   │────▶│  Filter  │
│  Jobs  │     │  Skills  │     │   Jobs   │     │   Jobs   │
└────────┘     └──────────┘     └──────────┘     └──────────┘
                                                        │
                                                        ▼
┌────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Alert  │◀────│ Retrieve │◀────│   Save   │◀────│Deduplicate│
│  User  │     │   New    │     │    DB    │     │   Jobs   │
└────────┘     └──────────┘     └──────────┘     └──────────┘
```

## Key Components

### Scrapers
- **BaseScraper**: Common functionality (rate limiting, robots.txt, HTTP)
- **RemoteOKScraper**: Works with JSON API ✅
- **IntershalaScraper**: Template for implementation
- **CompanyScraper**: Generic company career page scraper

### Intelligence
- **SkillExtractor**: Extracts skills from job descriptions using regex
- **SkillMatcher**: Calculates skill match using Jaccard similarity

### Scoring
- **RelevanceScorer**: Multi-factor scoring with configurable weights

### Filters
- **JobFilter**: Filters by score, type, location
- **JobDeduplicator**: Removes duplicates using fuzzy matching
- **JobPipeline**: Combines filtering and deduplication

### Storage
- **JobStorage**: SQLite operations, history tracking, statistics

### Alerts
- **ConsoleAlerter**: Rich terminal output
- **EmailAlerter**: SMTP email notifications
- **AlertManager**: Manages all alert channels

### Scheduler
- **DiscoveryScheduler**: Manages scheduled runs with configurable intervals

## Configuration

All components read from `config.yaml`:

```yaml
user:          # User profile
scraping:      # Scraping behavior
sources:       # Job sources
scoring:       # Scoring weights
filtering:     # Filter criteria
alerts:        # Alert settings
scheduling:    # Timing configuration
taxonomy:      # Skills taxonomy
```

## Extension Points

1. **Add Scrapers**: Inherit from `BaseScraper`
2. **Custom Scoring**: Modify weights in config or extend `RelevanceScorer`
3. **New Filters**: Add methods to `JobFilter`
4. **Alert Channels**: Implement new alerters (SMS, Slack, etc.)
5. **Storage Backends**: Replace `JobStorage` with PostgreSQL, MongoDB, etc.
