import pytest
from rest_framework.test import APIClient

from tests.factories import (
    AdamFactory,
    CompanyFactory,
    MartinFactory,
    NekoSvanFactory,
    VadimFactory,
)


@pytest.fixture
def company():
    return CompanyFactory()


@pytest.fixture
def adam(company):
    return AdamFactory(company=company)


@pytest.fixture
def vadim():
    return VadimFactory()


@pytest.fixture
def martin():
    return MartinFactory()


@pytest.fixture
def nekosvan():
    return NekoSvanFactory()


@pytest.fixture
def api_client():
    """DRF APIClient for testing API endpoints"""
    return APIClient()


@pytest.fixture
def internal_user():
    """Internal user with permissions for testing"""
    return MartinFactory()
