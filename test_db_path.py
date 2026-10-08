"""
test_db_path.py
Proves get_db_path() obeys the override and never depends on
which folder the terminal happens to be in.
"""
import os

from utils import get_db_path

def test_override_wins(monkeypatch, tmp_path):
    fake = str(tmp_path / "test.db")
    monkeypatch.setenv("SEPARAKA_DB_PATH", fake)

    assert get_db_path() == fake

def test_local_path_ignores_current_folder(monkeypatch, tmp_path):
    monkeypatch.delenv("SEPARAKA_DB_PATH", raising=False)
    monkeypatch.chdir(tmp_path)

    path = get_db_path()

    assert os.path.isabs(path)
    assert os.path.basename(path) == "taxi.db"
    assert os.path.dirname(path) != str(tmp_path)

def test_setup_uses_the_same_function():
    import setup_taxi_db
    import utils

    assert setup_taxi_db.get_db_path is utils.get_db_path