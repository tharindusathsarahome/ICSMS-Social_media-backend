# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from main import app

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client