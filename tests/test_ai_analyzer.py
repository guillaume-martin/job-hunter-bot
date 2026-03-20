import json
from unittest.mock import MagicMock, mock_open, patch

import pytest
from requests.exceptions import RequestException

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


# ---------------------------------------------------------------------------
# analyze_job
# ---------------------------------------------------------------------------


def test_analyze_job_returns_parsed_dic(analyzer):
    """analyze_job should return a parsed dict from the API response content."""
    # Setup
    expected = {"match_score": "85/100", "recommendation": "Apply"}

    analyzer._build_message = MagicMock(return_value="Analyze this job and resume.")

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{"message": {"content": json.dumps(expected)}}]
    }

    # Exercise
    with patch("src.ai_analyzer.request", return_value=mock_response):
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

    analyzer._build_message = MagicMock(return_value="Analyze this.")

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    # Content is a dict, not a string
    mock_response.json.return_value = {"choices": [{"message": {"content": expected}}]}

    # Exercise
    with patch("src.ai_analyzer.request", return_value=mock_response):
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


def test_analyze_job_returns_none_on_request_exception(analyzer):
    """analyze_job should return None when the API request fails."""
    # Setup
    analyzer._build_message = MagicMock(return_value="Analyze this.")

    # Exercise
    with patch(
        "src.ai_analyzer.request", side_effect=RequestException("Connection refused")
    ):
        result = analyzer.analyze_job("Resume text", "Job description text")

    # Verify
    # Exception is caught internally, None returned
    assert result is None


def test_analyze_job_returns_none_on_invalid_response(analyzer):
    """analyze_job should return None when the response structure is unexpected."""
    # Setup
    # Response is missing the "choices" key
    analyzer._build_message = MagicMock(return_value="Analyze this.")

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"unexpected_key": "unexpected_value"}

    # Exercise
    with patch("src.ai_analyzer.request", return_value=mock_response):
        result = analyzer.analyze_job("Resume text", "Job description text")

    # Verify
    # KeyError is caught internally, None returned
    assert result is None
