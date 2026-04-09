import unittest

import pytest
from rest_framework.test import APIClient

from core.tests.constants import DEDUPLICAR_ENDPOINT


@pytest.mark.django_db
class BaseProcessoViewsetTests(unittest.TestCase):
    endpoint = DEDUPLICAR_ENDPOINT

    def make_api_client(self) -> APIClient:
        return APIClient()

    def post_deduplicar(self, api_client: APIClient, payload: list[dict]):
        return api_client.post(self.endpoint, payload, format="json")
