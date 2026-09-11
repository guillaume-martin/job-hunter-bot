import json
from unittest.mock import MagicMock, mock_open, patch

import pytest
from litellm.exceptions import APIError, RateLimitError

from src.ai_analyzer import AIAnalyzer

# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def analyzer() -> AIAnalyzer:
    """Provide a fresh AIAnalyzer instance with dummy config for each test."""
    return AIAnalyzer(
        api_key="dummy_key",  # pragma: allowlist secret
        provider="dummy_provider",
        model="dummy_model",
        prompt_file="dummy_prompt.txt",
    )


def make_mock_response(content) -> MagicMock:
    """Build a mock mimicking litellm's ModelResponse shape."""
    mock_message = MagicMock()
    mock_message.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


# ---------------------------------------------------------------------------
# _build_system_instructions
# ---------------------------------------------------------------------------


def test_build_system_instructions_replaces_placehoders(analyzer):
    """Test that _build_system_instructions replaces $resume placeholder."""

    # Setup
    mock_prompt = "Resume: $resume"
    test_resume = "Python Developer with 5 years of experience."

    # Exercise
    with patch("builtins.open", mock_open(read_data=mock_prompt)):
        message = analyzer._build_system_instructions(test_resume)

    # Verify
    assert "$resume" not in message
    assert test_resume in message


def test_build_system_instructions_raises_on_empty_resume(analyzer):
    """_build_system_instructions should raise ValueError when resume is empty."""
    with pytest.raises(ValueError, match="Resume must not be empty"):
        analyzer._build_system_instructions("")


def test_build_system_instructions_raises_on_missing_prompt_file(analyzer):
    """_build_system_instructions should raise FileNotFoundError when the prompt file is
    missing.
    """
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError, match="Prompt file not found"):
            analyzer._build_system_instructions("resume text")


# ---------------------------------------------------------------------------
# analyze_job
# ---------------------------------------------------------------------------


def test_analyze_job_returns_parsed_dic(analyzer):
    """analyze_job should return a parsed dict from the API response content."""
    # Setup
    expected = {"match_score": "85/100", "recommendation": "Apply"}

    analyzer._build_system_instructions = MagicMock(
        return_value="Analyze this job and resume."
    )

    mock_response = make_mock_response(json.dumps(expected))

    # Exercise
    with patch("src.ai_analyzer.completion", return_value=mock_response):
        result = analyzer.analyze_job("Resume text", "Job description text")

    # Verify
    assert isinstance(result, dict)
    assert result == expected
    assert result["match_score"] == "85/100"
    assert result["recommendation"] == "Apply"


def test_analyze_job_handles_content_already_dict(analyzer):
    """analyze_job should handle responses where content is already a dict."""
    # Setup
    # Some APIs return content as a dict, not a JSON string
    expected = {"match_score": "90/100", "recommendation": "Strong Apply"}

    analyzer._build_system_instructions = MagicMock(return_value="Analyze this.")

    mock_response = make_mock_response(expected)

    # Exercise
    with patch("src.ai_analyzer.completion", return_value=mock_response):
        result = analyzer.analyze_job("Resume text", "Job description text")

    # Verify
    assert result == expected


def test_analyze_job_raises_on_empty_inputs(analyzer):
    """analyze_job should raise ValueError when resume or job description is empty."""
    # Setup
    # No set up needed
    # Exercise
    with pytest.raises(
        ValueError, match="Resume and job description must not be empty"
    ):
        analyzer.analyze_job("", "Some job description")

    with pytest.raises(
        ValueError, match="Resume and job description must not be empty"
    ):
        analyzer.analyze_job("Some resume", "")


def test_analyze_job_returns_none_on_api_error(analyzer):
    """analyze_job should return None when the API returns an error."""
    # Setup
    analyzer._build_system_instructions = MagicMock(return_value="Analyze this.")
    api_error = APIError(
        status_code=500,
        message="API Error occurred",
        llm_provider="dummy_provider",
        model="dummy_model",
    )

    # Exercise
    with patch("src.ai_analyzer.completion", side_effect=api_error):
        result = analyzer.analyze_job("Resume text", "Job description text")

    # Verify
    assert result is None


def test_analyze_job_returns_none_on_rate_limit_error(analyzer):
    """analyze_job should return None when the API returns a rate limit error."""
    # Setup
    analyzer._build_system_instructions = MagicMock(return_value="Analyze this.")
    rate_limit_error = RateLimitError(
        message="Rate limit exceeded",
        llm_provider="dummy_provider",
        model="dummy_model",
    )

    # Exercise
    with patch("src.ai_analyzer.completion", side_effect=rate_limit_error):
        result = analyzer.analyze_job("Resume text", "Job description text")

    # Verify
    assert result is None


def test_analyze_job_returns_none_on_empty_choices(analyzer):
    """analyze_job should return None when the API response has no choices."""
    # Setup
    analyzer._build_system_instructions = MagicMock(return_value="Analyze this.")
    mock_response = MagicMock()
    mock_response.choices = []  # Simulate no choices returned

    # Exercise
    with patch("src.ai_analyzer.completion", return_value=mock_response):
        result = analyzer.analyze_job("Resume text", "Job description text")

    # Verify
    assert result is None
