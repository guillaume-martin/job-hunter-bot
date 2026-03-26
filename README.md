# Job Hunter Bot

<!-- Status -->
[![Lint](https://github.com/guillaume-martin/job-hunter-bot/actions/workflows/lint.yml/badge.svg)](https://github.com/guillaume-martin/job-hunter-bot/actions/workflows/lint.yml)
[![Unit Tests](https://github.com/guillaume-martin/job-hunter-bot/actions/workflows/tests.yml/badge.svg)](https://github.com/guillaume-martin/job-hunter-bot/actions/workflows/tests.yml)
[![Last Commit](https://img.shields.io/github/last-commit/guillaume-martin/job-hunter-bot)](https://github.com/guillaume-martin/job-hunter-bot/commits/main)

<!-- Stack -->
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/Poetry-package%20manager-blue?logo=poetry)](https://python-poetry.org/)
[![AWS](https://img.shields.io/badge/AWS-DynamoDB%20%7C%20SES-orange)](https://aws.amazon.com/)

<!-- License -->
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)

Job hunting is time-consuming — finding openings that actually match your skills requires
checking multiple boards every day. Job Hunter Bot automates that process by scraping remote
job boards, scoring each listing against your resume using AI, and delivering only the best
matches to your inbox.

Some job boards let recruiters refresh their listings daily to stay at the top of search
results. To avoid seeing the same listings every day, the bot tracks previously scraped jobs
in a DynamoDB cache and filters them out on subsequent runs.

---

## 📚 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Adding a New Scraper](#-adding-a-new-scraper)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- Scrapes multiple remote job boards (Remotive, RemoteOK, We Work Remotely, Working Nomads, Truly Remote, 104)
- Scores each listing against your resume using AI to surface the best matches
- Filters by search term and configurable per-scraper locations
- Tracks previously seen listings in DynamoDB to avoid duplicates across daily runs
- Delivers new matches by email via AWS SES
- Configurable retention window — cached listings expire automatically via DynamoDB TTL
- Extensible scraper architecture: add a new board by implementing a single base class

[Top](#-table-of-contents)

---

## 📸 Demo

The bot generates a dated Markdown file for each run. Example output:

| Title | Company | Match Score | Date Published | Missing Required Skills |
| ----- | ------- | ----------- | -------------- | ----------------------- |
| [Senior Backend Engineer](https://example.com/jobs/123) | Acme Corp | 92/100 | 2025-12-08 | |
| [Staff Platform Engineer](https://example.com/jobs/456) | Globex Inc | 85/100 | 2025-12-08 | Kubernetes, Helm |
| [Cloud Infrastructure Engineer](https://example.com/jobs/789) | Initech | 78/100 | 2025-12-07 | Terraform, AWS CDK |
| [DevOps Engineer](https://example.com/jobs/101) | Umbrella Corp | 72/100 | 2025-12-07 | Go Programming Language, CI/CD Pipeline |
| [Site Reliability Engineer](https://example.com/jobs/112) | Hooli | 65/100 | 2025-12-06 | Expert-level Kubernetes, On-call experience |

[Top](#-table-of-contents)

---

## 🔄 How It Works

```mermaid
flowchart TD

A[job_search.py] -->|1 - search terms| B[ScraperFactory]
B --> C[Scraper Instance]
C <-->|"Deduplicate (104 only)"| D[(DynamoDB)]
C -->|2 - raw jobs| A
A -->|3 - job + resume| E[AIAnalyzer]
E -->|4 - match score| A
A -->|5 - selected jobs| G[Output]
G -->|cloud| F[Mailer]
G -->|local| H[File]
F -->|email| I[AWS SES]
```

[Top](#-table-of-contents)

---

## 🔧 Tech Stack

| Layer                 | Technology                         |
|-----------------------|------------------------------------|
| Language              | Python 3.11+                       |
| Dependency management | Poetry                             |
| Scraping              | Requests, BeautifulSoup4, Selenium |
| Storage               | AWS DynamoDB                       |
| Email delivery        | AWS SES                            |
| Infrastructure        | Terraform + Terragrunt             |
| Containerization      | Docker                             |
| CI/CD                 | GitHub Actions                     |
| Testing               | Pytest                             |

[Top](#-table-of-contents)

---

## 📁 Project Structure

```txt
job-hunter-bot/
├── .github/
│   └── workflows/          # GitHub Actions pipelines
├── docker/                 # Dockerfile and compose files
├── iac/
│   └── environments/       # Terraform + Terragrunt configuration
├── src/
│   ├── config.py                    # Centralized configuration
│   ├── search_config.template.yaml  # Search config template
│   ├── scrapers/
│   │   ├── base_scraper.py # Abstract base class for all scrapers
│   │   ├── remotive.py
│   │   ├── remoteok.py
│   │   ├── wwr.py
│   │   └── ...
│   └── ...
├── tests/
│   ├── e2e/
│   ├── integration/
│   └── unit/
├── Makefile
├── pyproject.toml
└── README.md
```

[Top](#-table-of-contents)

---

## 🚀 Getting Started

### 📋 Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- AWS credentials configured (`~/.aws/credentials` or environment variables)
- A DynamoDB table for job caching
- An AWS SES verified sender address

### 📦 Installation

```bash
git clone https://github.com/guillaume-martin/job-hunter-bot.git
cd job-hunter-bot
poetry install
```

### ⚙️ Configuration

#### Environment Variables

1. Create the `.env` file

```bash
cp src/template.env src/.env
```

2. Update the variables
Open `src/.env` and fill in the required values. Every variable in the file is required unless marked optional.

> **Never commit `.env` to version control.**

#### Search Configuration

1. Create the search config file:

```bash
cp src/search_config.template.yaml src/search_config.yaml
```

2. Edit `src/search_config.yaml` to set your search terms, target job boards, freshness window, and per-scraper location filters:

```yaml
searches:
  - "backend engineer"
  - "data engineer"

sites:
  - "weworkremotely"
  - "remotive"
  - "remoteok"

since: 3

# Per-scraper location filters (optional)
workingnomads:
  locations:
    - "Anywhere"
    - "Asia"
  url_locations: "taiwan,-province-of-china"

remoteok:
  locations:
    - "Worldwide"
    - "region_AS"

remotive:
  locations:
    - "Worldwide"
    - "APAC"

trulyremote:
  locations:
    - "Anywhere in the world"
    - "Asia"
```

Valid site names: `104`, `remoteok`, `remotive`, `trulyremote`, `workingnomads`, `weworkremotely`

> If the file is missing, the bot falls back to built-in defaults. Per-scraper location sections are optional — each scraper uses sensible defaults when omitted.

### 💻 Running Locally

```bash
# Build the Docker image
make build

# Run the bot
make run
```

The `run` target mounts your local AWS credentials into the container, so no additional AWS configuration is needed inside Docker.

### ☁️ Running In The Cloud

🚧 Coming Soon

### 🧪 Run The Tests

```bash
poetry run pytest tests/unit/ -v

# Or via Makefile:
make test
```

[Top](#-table-of-contents)

---

## 🔌 Adding a New Scraper

1. Create a new file in `src/scrapers/`, e.g. `myboard.py`
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

[Top](#-table-of-contents)

---

## 📍 Roadmap

- [x] Refactor all scrapers to use the new `BaseScraper` architecture
- [x] Expand unit test coverage across all scrapers
- [ ] Refactor `remoteco.py` legacy scraper into `BaseScraper` architecture
- [ ] Add integration tests for all scrapers
- [ ] Complete IaC scripts with Terraform and Terragrunt
- [ ] Build full CI/CD pipeline with GitHub Actions (lint → test → deploy)
- [ ] Add monitoring and alerting (CloudWatch metrics, error notifications)

[Top](#-table-of-contents)

---

## 🤝 Contributing

Issues and pull requests are welcome. Please open an issue first to discuss
what you'd like to change.

[Top](#-table-of-contents)

---

## 📄 License

Distributed under the GPL-3.0 License. See [LICENSE](LICENSE) for details.

[Top](#-table-of-contents)
