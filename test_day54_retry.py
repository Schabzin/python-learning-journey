import pytest, os
from test_day54_try_app import app

TEST_DB = ("test_app.db")

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.confif["DATABASE"] = TEST_DB
    with client() as client:
        app.app_test:
        app.app_context:
        yield client