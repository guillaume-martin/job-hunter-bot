import src.job_search as job_search


def test_remove_duplicates_with_urls():
    """Test that remove_duplicates removes jobs with duplicate URLs."""

    # Setup
    jobs = [
        {
            "company": "Acme Inc",
            "title": "Software Engineer",
            "url": "https://example.com/job1",
            "date_published": "2024-06-01",
        },
        {
            "company": "Acme Inc",
            "title": "Software Engineer",
            "url": "https://example.com/job1",
            "date_published": "2024-06-01",
        },
        {
            "company": "Globex Corp",
            "title": "Data Scientist",
            "url": "https://example.com/job2",
            "date_published": "2024-06-02",
        },
    ]

    # Exercise
    single_jobs_list = job_search.remove_duplicates(jobs)

    # Verify
    assert len(single_jobs_list) == 2
    assert single_jobs_list == [
        {
            "company": "Acme Inc",
            "title": "Software Engineer",
            "url": "https://example.com/job1",
            "date_published": "2024-06-01",
        },
        {
            "company": "Globex Corp",
            "title": "Data Scientist",
            "url": "https://example.com/job2",
            "date_published": "2024-06-02",
        },
    ]


def test_remove_duplicates_with_missing_urls():
    """Test that remove_duplicates removes jobs with duplicate company + title"""

    # Setup
    jobs = [
        {"url": "missing", "title": "Job 1", "company": "Acme"},
        {"url": "missing", "title": "Job 1", "company": "Acme"},  # Duplicate
        {"url": "missing", "title": "Job 2", "company": "Acme"},
    ]

    # Exercise
    single_jobs_list = job_search.remove_duplicates(jobs)

    # Verify
    assert len(single_jobs_list) == 2
    assert single_jobs_list == [
        {"url": "missing", "title": "Job 1", "company": "Acme"},
        {"url": "missing", "title": "Job 2", "company": "Acme"},
    ]


def test_jobs_to_html_returns_string():
    """jobs_to_html should return a string containing the HTML script"""

    # Setup
    jobs = [
        {
            "url": "https://acme.com",
            "title": "job title",
            "company": "Acme, Inc.",
            "date_published": "2022-04-29",
        }
    ]

    # Exercise
    result = job_search.jobs_to_html(jobs)

    # Verify
    assert isinstance(result, str)


def test_jobs_to_html_contails_job_data():
    """jobs_to_html should return an HTML table with all job fields populated."""
    # Setup
    jobs = [
        {
            "url": "https://acme.com/job1",
            "title": "Engineer",
            "company": "Acme, Inc.",
            "date_published": "2022-04-29",
            "evaluation": {"match_score": "90/100", "missing_required": ["Docker"]},
        }
    ]

    # Exercise
    result = job_search.jobs_to_html(jobs)

    # Verify
    assert "<table>" in result
    assert "Engineer" in result
    assert "Acme, Inc." in result
    assert "90/100" in result
    assert "Docker" in result
    assert "href='https://acme.com/job1'" in result


def test_find_jobs_calls_scrappers(monkeypatch):
    """find_jobs should call the configured scrapers and return combined results"""
    # setup
    calls: list[tuple[str, str]] = []
    fake_sites = ["siteA", "siteB"]

    class FakeScraper:
        def __init__(self, site):
            self.site = site

        def get_jobs(self, term):
            calls.append((self.site, term))
            self.jobs = []

        def remove_older_jobs(self, days_threshold):
            pass

    def fake_get_scraper(site):
        return FakeScraper(site)

    search = ["python", "sql"]

    # Patch job_search module-level symbols that find_jobs uses
    monkeypatch.setattr(job_search, "get_scraper", fake_get_scraper)
    monkeypatch.setattr(job_search.Config, "SITES", fake_sites)

    # Exercise
    job_search.find_jobs(searches=search)

    # Verify
    expected_calls = [(s, t) for t in search for s in fake_sites]
    assert calls == expected_calls


def test_save_jobs_to_file_create_file(tmp_path, monkeypatch):
    """_save_jobs_to_file should write a markdown file to the configured output path.

    Tests the file-writing unit directly rather than going through main(),
    which would require patching unrelated dependencies (AIAnalyzer, resume, etc.).
    """

    # Setting
    monkeypatch.setattr(job_search.Config, "OUTPUT_PATH", str(tmp_path))
    monkeypatch.setattr(job_search.Config, "OUTPUT_FILE", "jobs.md")

    # Mock the jobs and other dependencies
    mock_jobs = [
        {
            "url": "https://example.com/job1",
            "title": "Job 1",
            "company": "Acme",
            "evaluation": {"match_score": "85/100", "missing_required": []},
        },
    ]

    # Exercise
    job_search._save_jobs_to_file(mock_jobs, suffix="selected", date="2026-03-19")

    # Verify
    # Check that the file exists
    expected_file = tmp_path / "2026-03-19-jobs-selected.md"
    assert expected_file.exists(), f"Expected file not found: {expected_file}"

    # Verify the content is valid
    content = expected_file.read_text(encoding="utf-8")
    assert "Job 1" in content
    assert "Acme" in content
    assert "85/100" in content


def test_jobs_to_markdown_return_string():
    """Test that jobs_to_markdown returns a file"""
    # Setup
    mock_jobs = [
        {
            "url": "https://example.com/job1",
            "title": "Job 1",
            "company": "Acme",
            "evaluation": {"match_score": "85/100", "missing_required": []},
        },
        {
            "url": "https://example.com/job2",
            "title": "Job 2",
            "company": "Acme",
            "evaluation": {"match_score": "75/100", "missing_required": ["Python"]},
        },
    ]

    # Exercise
    result = job_search.jobs_to_markdown(mock_jobs)

    # Verify
    assert isinstance(result, str)


def test_jobs_to_markdown_contains_job_data():
    """jobs_to_markdown should return a Markdown table with all job fields."""
    # Setup
    jobs = [
        {
            "url": "https://example.com/job1",
            "title": "Job 1",
            "company": "Acme",
            "evaluation": {"match_score": "85/100", "missing_required": ["Python"]},
        },
    ]

    # Exercise
    result = job_search.jobs_to_markdown(jobs)

    # Verify
    assert result.startswith("|Title|")  # header row present
    assert result.count("\n") >= 3  # header + separator + 1 data row
    assert "Job 1" in result
    assert "Acme" in result
    assert "85/100" in result
    assert "Python" in result


def test_jobs_to_markdown_empty_list():
    """jobs_to_markdown with no jobs should still return a valid header."""
    # Setup
    # Nothing to set up

    # Exercise
    result = job_search.jobs_to_markdown([])

    # Verify
    assert result.startswith("|Title|")
    # Only header and separator — no data rows
    assert result.count("\n") == 2


def test_select_jobs_above_threshold(monkeypatch, fake_analyzer):
    """Jobs scoring at or above APPLY_THRESHOLD should be selected"""
    # Setup
    monkeypatch.setattr(job_search.Config, "APPLY_THRESHOLD", 80)

    jobs = [{"title": "Job 1", "company": "Acme", "description": "Some description"}]

    # Exercise
    selected, rejected = job_search.select_jobs(jobs, fake_analyzer, "my resume")

    # Verify
    assert len(selected) == 1
    assert len(rejected) == 0
    assert fake_analyzer.called  # analyzer should have been called


def test_reject_jobs_below_threshold(monkeypatch, fake_analyzer):
    """Jobs scoring below APPLY_THRESHOLD should be rejected."""
    # Setup
    monkeypatch.setattr(job_search.Config, "APPLY_THRESHOLD", 80)

    # Override the default return value for this specific test
    fake_analyzer.return_value = {"match_score": "40/100", "missing_required": []}

    jobs = [{"title": "Job 1", "company": "Acme", "description": "Some description"}]

    # Exercise
    selected, rejected = job_search.select_jobs(jobs, fake_analyzer, "my resume")

    # Verify
    assert len(selected) == 0
    assert len(rejected) == 1
    assert fake_analyzer.called  # analyzer should have been called


def test_select_jobs_no_description_is_selected(monkeypatch, fake_analyzer):
    """Jobs without a description should be selected for manual review."""
    # Setup
    monkeypatch.setattr(job_search.Config, "APPLY_THRESHOLD", 80)

    jobs = [{"title": "Job 1", "company": "Acme", "description": ""}]

    # Exercise
    selected, rejected = job_search.select_jobs(jobs, fake_analyzer, "my resume")

    # Verify
    assert len(selected) == 1
    assert len(rejected) == 0
    assert selected[0]["evaluation"] == "manual"
    assert not fake_analyzer.called  # analyzer should not have been called
