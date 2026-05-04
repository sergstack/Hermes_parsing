from datetime import date
from unittest.mock import MagicMock

import pytest

from app.dates import MonthPeriod


@pytest.fixture
def sample_period():
    return MonthPeriod(start=date(2026, 3, 1), end=date(2026, 3, 31))


@pytest.fixture
def mock_page():
    return MagicMock()


@pytest.fixture
def mock_session(mock_page):
    session = MagicMock()
    session.page = mock_page
    return session
