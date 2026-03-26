import logging

from src.config import _load_search_config


def test_missing_file(caplog, config_path):
    """When the search_config.yaml file doesn't exist, the function should return
    an empty dictionary and log a warning.
    """
    # Setup
    config_path("missing.yaml")

    # Exercise
    with caplog.at_level(logging.WARNING, logger="src.config"):
        result = _load_search_config()

    # Verify
    assert result == {}
    assert "Search config file not found" in caplog.text


def test_valid_yaml_file_returns_dict(config_path):
    """When the search_config.yaml file is valid, the function returns a dictionary"""
    # Setup
    path = config_path()  # uses default "search_config.yaml"
    path.write_text('searches:\n - "data engineer"')

    # Exercise
    result = _load_search_config()

    # Verify
    assert result == {"searches": ["data engineer"]}


def test_yaml_file_empty(config_path):
    """When the search_config.yaml file is empty, the function returns {}"""
    # Setup
    path = config_path("search_config.yaml")
    path.write_text("")

    # Exercise
    result = _load_search_config()

    # Verify
    assert result == {}


def test_malformed_yaml(caplog, config_path):
    """A malformed yaml file returns an empty dict and log an error"""
    # Setup
    path = config_path("search_config.yaml")
    path.write_text("{invalid: [}")

    # Exercise
    with caplog.at_level(logging.ERROR, logger="src.config"):
        result = _load_search_config()

    # Verify
    assert result == {}
    assert "Failed to parse" in caplog.text
