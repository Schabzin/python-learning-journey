import sqlite3
import bcrypt
import pytest
import setup_taxi_db

CI_PASSWORD = "ci-only-pass-123"

@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    db = tmp_path / "practice.db"
    monkeypatch.setenv("SEPARAKA_DB_PATH", str(db))
    monkeypatch.delenv("SEPARAKA_SEED_DEFAULTS", raising=False)
    monkeypatch.delenv("DEFAULT_USER_PASSWORD", raising=False)
    setup_taxi_db.run_migrations()
    return db


def user_count(db):
    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count


def stored_hash(db, username):
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT password FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row[0]


def test_no_switch_creates_no_users(fresh_db):
    assert user_count(fresh_db) == 0


def test_switch_without_password_refuses(fresh_db, monkeypatch):
    monkeypatch.setenv("SEPARAKA_SEED_DEFAULTS", "1")
    with pytest.raises(RuntimeError):
        setup_taxi_db.create_default_users()
    assert user_count(fresh_db) == 0


def test_switch_with_password_creates_hashed_users(fresh_db, monkeypatch):
    monkeypatch.setenv("SEPARAKA_SEED_DEFAULTS", "1")
    monkeypatch.setenv("DEFAULT_USER_PASSWORD", CI_PASSWORD)
    assert setup_taxi_db.create_default_users() == 4
    saved = stored_hash(fresh_db, "marshall1")
    assert saved != CI_PASSWORD.encode()
    assert bcrypt.checkpw(CI_PASSWORD.encode(), saved)


def test_existing_user_password_is_never_overwritten(fresh_db, monkeypatch):
    real = bcrypt.hashpw(b"owners-own-password", bcrypt.gensalt())
    conn = sqlite3.connect(fresh_db)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("chahane", real, "owner"))
    conn.commit()
    conn.close()
    monkeypatch.setenv("SEPARAKA_SEED_DEFAULTS", "1")
    monkeypatch.setenv("DEFAULT_USER_PASSWORD", CI_PASSWORD)
    assert setup_taxi_db.create_default_users() == 3
    assert bcrypt.checkpw(b"owners-own-password", stored_hash(fresh_db, "chahane"))