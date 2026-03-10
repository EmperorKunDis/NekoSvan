import pytest

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
