"""
conftest.py
pytest loads this file automatically. Fixtures defined here are
available to every test file in this folder, with no import needed.
"""
import os
import runpy
import sqlite3
import pytest
from utils import get_db_path

HERE = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def test_db(monkeypatch, tmp_path):
    """A full app database, built by the REAL setup script, in a temp folder."""
    path = str(tmp_path / "separaka_test.db")
    monkeypatch.setenv("SEPARAKA_DB_PATH", path)
    assert get_db_path() == path

    runpy.run_path(os.path.join(HERE, "setup_taxi_db.py"), run_name="__main__")

    conn = sqlite3.connect(path)
    with conn:
        conn.execute("INSERT INTO taxis (plate, driver_username) VALUES (?, ?)",
                     ("TEST01GP", "tester"))
        conn.execute("INSERT INTO taxis (plate, driver_username) VALUES (?, ?)",
                     ("OTHER2GP", "someone_else"))
    conn.close()
    return path