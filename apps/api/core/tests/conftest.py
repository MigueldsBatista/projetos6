import os

import pytest
from rest_framework.test import APIClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()
