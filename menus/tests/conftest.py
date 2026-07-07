import pytest


@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker):
    """Force the test suite to use an in-memory SQLite database to avoid permission errors."""
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
