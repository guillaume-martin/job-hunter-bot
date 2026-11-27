"""Reproduces the reported failure: LLM returns non-plain JSON and the bot crashed
with "TypeError: string indices must be integers, not 'str'" at job_search.py:215.
"""

import json
from unittest.mock import MagicMock, patch

import src.job_search as job_search
from src.ai_analyzer import AIAnalyzer


def _mock_response(content) -> MagicMock:
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _analyzer() -> AIAnalyzer:
    return AIAnalyzer(
        api_key="dummy",  # pragma: allowlist secret
        provider="mistral",
        model="mistral-small-latest",
        prompt_file="dummy_prompt.txt",
    )


def test_fenced_json_end_to_end_selected():
    """Fenced JSON (the reported failure mode) must parse and select the job."""
    analyzer = _analyzer()
    fenced = (
        "```json\n"
        + json.dumps({"match_score": "85/100", "missing_required": ["Kubernetes"]})
        + "\n```"
    )
    job = {
        "title": "Backend Engineer",
        "company": "Acme",
        "url": "http://x",
        "description": "desc",
    }
    with (
        patch.object(analyzer, "_build_system_instructions", return_value="prompt"),
        patch("src.ai_analyzer.completion", return_value=_mock_response(fenced)),
    ):
        selected, rejected = job_search.select_jobs([job], analyzer, "resume")

    assert len(selected) == 1
    assert len(rejected) == 0
    assert selected[0]["evaluation"]["match_score"] == "85/100"


def test_raw_string_evaluation_rejected_without_typeerror():
    """A raw string evaluation must be rejected gracefully, not raise TypeError."""
    analyzer = _analyzer()
    job = {
        "title": "Job2",
        "company": "Acme",
        "url": "http://y",
        "description": "desc",
        "evaluation": "some raw unparsed LLM string",
    }
    selected, rejected = job_search.select_jobs([job], analyzer, "resume")
    assert len(selected) == 0
    assert len(rejected) == 1


def test_unparseable_llm_response_returns_none():
    """Plain prose with no JSON must return None so the caller rejects cleanly."""
    analyzer = _analyzer()
    with (
        patch.object(analyzer, "_build_system_instructions", return_value="prompt"),
        patch(
            "src.ai_analyzer.completion",
            return_value=_mock_response("The candidate looks good, 85/100."),
        ),
    ):
        result = analyzer.analyze_job("resume", "job description")
    assert result is None
