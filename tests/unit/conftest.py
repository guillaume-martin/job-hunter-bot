import pytest


def pytest_collection_modifyitems(items):
    """Automatically mark all tests in this folder as unit tests."""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)


@pytest.fixture
def config_path(monkeypatch, tmp_path):
    def _set(filename="search_config.yaml"):
        path = tmp_path / filename
        monkeypatch.setattr("src.config._SEARCH_CONFIG_PATH", str(path))
        return path

    return _set
