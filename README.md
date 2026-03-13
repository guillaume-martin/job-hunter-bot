# Job Hunter Bot

A Python bot that scrapes remote job boards, deduplicates results against a DynamoDB cache, and delivers new listings by email.

---

## Features

- Scrapes multiple remote job boards (Remotive, RemoteOK, We Work Remotely, Working Nomads, Truly Remote, 104)
- Filters jobs by search term and location (Worldwide / APAC)
- Deduplicates against a DynamoDB cache to avoid re-sending known listings
- Sends new listings by email via AWS SES
- Configurable retention window — old listings expire automatically via DynamoDB TTL
- Extensible scraper architecture: add a new board by implementing a single base class

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Job Hunter Bot                    │
│                                                     │
│  ┌────────────────┐      ┌───────────────────────┐  │
│  │ ScraperFactory │────▶│ BaseScraper (ABC)     │  │
│  └────────────────┘      │  - get_jobs()         │  │
│                          │  - extract_company()  │  │
│                          │  - extract_title()    │  │
│                          │  - ...                │  │
│                          └──────────┬────────────┘  │
│                                     │ implements    │
│              ┌──────────────────────┼──────────┐    │
│              ▼          ▼           ▼          ▼    │
│         Remotive   RemoteOK   WorkingNomads   ...   │
└──────────────────────────┬──────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       ┌─────────────┐          ┌──────────────┐
       │  DynamoDB   │          │   AWS SES    │
       │ (job cache) │          │  (delivery)  │
       └─────────────┘          └──────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Dependency management | Poetry |
| Scraping | Requests, BeautifulSoup4, Selenium |
| Storage | AWS DynamoDB |
| Email delivery | AWS SES |
| Infrastructure | Terraform + Terragrunt |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Testing | Pytest |

---

## Project Structure

```
job-hunter-bot/
├── .github/
│   └── workflows/          # GitHub Actions pipelines
├── docker/                 # Dockerfile and compose files
├── iac/
│   └── environments/       # Terraform + Terragrunt configuration
├── src/
│   ├── config.py           # Centralized configuration
│   ├── scrappers/
│   │   ├── base_scraper.py # Abstract base class for all scrapers
│   │   ├── remotive.py
│   │   ├── remoteok.py
│   │   ├── wwr.py
│   │   └── ...
│   └── ...
├── tests/
├── Makefile
├── pyproject.toml
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- AWS credentials configured (`~/.aws/credentials` or environment variables)
- A DynamoDB table for job caching
- An AWS SES verified sender address

### Installation

```bash
git clone https://github.com/guillaume-martin/job-hunter-bot.git
cd job-hunter-bot
poetry install
```

### Configuration

Create a `.env` file at the project root:

```env
# AWS
AWS_REGION=us-east-1

# DynamoDB
JOBS_TABLE=your-dynamodb-table-name

# Job retention
RETENTION_DAYS=30

# Email delivery
FROM_EMAIL=sender@example.com
TO_EMAIL=recipient@example.com
```

> **Never commit `.env` to version control.** A `.env.example` template is provided.

### Running locally

```bash
# Build the Docker image
make build

# Run the bot
make run
```

The `run` target mounts your local AWS credentials into the container, so no additional AWS configuration is needed inside Docker.

To run the tests directly:

```bash
poetry run pytest tests/
```

---

## Adding a New Scraper

1. Create a new file in `src/scrappers/`, e.g. `myboard.py`
2. Implement `BaseScraper`:

```python
from .base_scraper import BaseScraper

class MyBoardScraper(BaseScraper):

    def __init__(self):
        super().__init__(base_url="https://myboard.com", name="myboard")

    def get_jobs(self, term: str) -> list[dict]:
        ...

    def extract_company(self, job_element) -> str:
        ...

    def extract_title(self, job_element) -> str:
        ...

    def extract_url(self, job_element) -> str:
        ...

    def extract_date_published(self, job_element) -> str:
        ...

    def extract_job_description(self, job_url: str) -> str:
        ...
```

3. Register it in `scraper_factory.py`:

```python
from .myboard import MyBoardScraper

scrapers = {
    ...
    "myboard": MyBoardScraper,
}
```

---

## Roadmap

- [ ] Refactor all scrapers to use the new `BaseScraper` architecture
- [ ] Expand unit test coverage across all scrapers
- [ ] Complete IaC scripts with Terraform and Terragrunt
- [ ] Build full CI/CD pipeline with GitHub Actions (lint → test → deploy)
- [ ] Add monitoring and alerting (CloudWatch metrics, error notifications)

