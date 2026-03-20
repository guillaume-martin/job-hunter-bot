from unittest.mock import mock_open, patch

import pytest

from src.ai_analyzer import AIAnalyzer

# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def analyzer() -> AIAnalyzer:
    """Provide a fresh AIAnalyzer instance with dummy config for each test."""
    return AIAnalyzer(
        api_key="dummy_key",  # pragma: allowlist secret
        model="dummy_model",
        api_url="https://example.com/ai",
        prompt_file="dummy_prompt.txt",
    )


# ---------------------------------------------------------------------------
# _build_message
# ---------------------------------------------------------------------------


def test_build_message_replaces_placehoders(analyzer):
    """Test that _build_message replaces $resume and $job_description placeholders."""

    # Setup
    mock_prompt = "Job Description: $job_description Resume: $resume"
    test_resume = "Python Developer with 5 years of experience."
    test_job_description = "Backend Engineer (Python, Django, PostgreSQL)."

    # Exercise
    with patch("builtins.open", mock_open(read_data=mock_prompt)):
        message = analyzer._build_message(test_resume, test_job_description)

    # Verify
    assert "$resume" not in message
    assert "$job_description" not in message
    assert test_resume in message
    assert test_job_description in message


def test_build_message_raises_on_empty_resume(analyzer):
    """_build_message should raise ValueError when resume is empty."""
    with pytest.raises(
        ValueError, match="Resume and job description must not be empty"
    ):
        analyzer._build_message("", "Some job description")


def test_build_message_raises_on_empty_job_description(analyzer):
    """_build_message should raise ValueError when job description is empty."""
    with pytest.raises(
        ValueError, match="Resume and job description must not be empty"
    ):
        analyzer._build_message("Some resume", "")


def test_build_message_raises_on_missing_prompt_file(analyzer):
    """_build_message should raise FileNotFoundError when the prompt file is
    missing.
    """
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError, match="Prompt file not found"):
            analyzer._build_message("resume text", "job description text")
