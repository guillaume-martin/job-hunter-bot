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
