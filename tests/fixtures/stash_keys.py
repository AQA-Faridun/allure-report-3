import pytest

PHASE_REPORTS_KEY = pytest.StashKey[dict[str, pytest.TestReport]]()
ALLURE_ENV_KEY = pytest.StashKey[dict[str, str]]()
