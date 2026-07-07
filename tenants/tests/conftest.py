import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from tenants.domain.entities import TenantEntity


@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker):
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }




@pytest.fixture
def make_entity():
    """Factory fixture để tạo TenantEntity cho tests"""

    def _make(**kwargs):
        defaults = dict(
            id=1,
            uuid=uuid.uuid4(),
            code="DEMO",
            name="Demo Bus",
            plan="STANDARD",
            is_active=True,
            currency="VND",
            exchange_rate=Decimal("1.0000"),
            default_language="vi",
            timezone="Asia/Ho_Chi_Minh",
            primary_color="#3B82F6",
            max_users=10,
            max_branches=1,
            max_vehicles=50,
            subscription_started_at=None,
            subscription_expires_at=None,
            settings={},
            domain=None,
            logo_url=None,
        )
        defaults.update(kwargs)
        return TenantEntity(**defaults)

    return _make


@pytest.fixture
def mock_repos():
    """Factory fixture để tạo mock repositories"""

    def _mock():
        tenant_repo = MagicMock()
        audit_repo = MagicMock()
        return tenant_repo, audit_repo

    return _mock
