"""
test_join_lock.py
Proves the join route's lock: a marshal can only queue taxis from his OWN platform.
Every test runs on a throwaway practice database built by run_migrations(),
so the real taxi.db is never touched.
"""
import sqlite3
import pytest
from taxi_app import app
from setup_taxi_db import run_migrations


@pytest.fixture
def practice_db(tmp_path, monkeypatch):
    db_file = tmp_path / "practice.db"
    monkeypatch.setenv("SEPARAKA_DB_PATH", str(db_file))
    run_migrations()
    conn = sqlite3.connect(db_file)
    conn.execute("INSERT INTO platforms (id, name, rank_name) VALUES (901, 'Test Platform A', 'Test Rank')")
    conn.execute("INSERT INTO platforms (id, name, rank_name) VALUES (902, 'Test Platform B', 'Test Rank')")
    conn.execute("INSERT INTO users (username, password, role) "
                 "VALUES ('test_owner', 'not-a-real-password', 'owner')")
    conn.execute("INSERT INTO users (username, password, role, platform_id) "
                 "VALUES ('test_marshal_a', 'not-a-real-password', 'marshall', 901)")
    conn.execute("INSERT INTO users (username, password, role, platform_id) "
                 "VALUES ('test_marshal_none', 'not-a-real-password', 'marshall', NULL)")
    conn.execute("INSERT INTO taxis (id, plate, platform_id) VALUES (9001, 'OWN 001 GP', 901)")
    conn.execute("INSERT INTO taxis (id, plate, platform_id) VALUES (9002, 'OTHER 002 GP', 902)")
    conn.commit()
    conn.close()
    return db_file


@pytest.fixture
def client(practice_db):
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def log_in_as(client, username, role):
    with client.session_transaction() as sess:
        sess["user"] = username
        sess["role"] = role


def join(client, taxi_id):
    return client.post("/api/queue/join", data={"taxi_id": str(taxi_id), "layer": "Test Layer"})


def waiting_rows(db_file):
    conn = sqlite3.connect(db_file)
    rows = conn.execute("SELECT taxi_id, platform_id FROM queue WHERE status = 'waiting'").fetchall()
    conn.close()
    return rows


def test_other_platforms_taxi_is_refused(client, practice_db):
    log_in_as(client, "test_marshal_a", "marshall")
    response = join(client, 9002)
    assert response.status_code == 403
    assert "OTHER 002 GP is not on your platform" in response.get_json()["error"]
    assert waiting_rows(practice_db) == []


def test_own_platforms_taxi_joins(client, practice_db):
    log_in_as(client, "test_marshal_a", "marshall")
    response = join(client, 9001)
    assert response.status_code == 200
    assert waiting_rows(practice_db) == [(9001, 901)]


def test_marshal_without_platform_is_refused(client, practice_db):
    log_in_as(client, "test_marshal_none", "marshall")
    response = join(client, 9001)
    assert response.status_code == 403
    assert "not linked to a platform" in response.get_json()["error"]
    assert waiting_rows(practice_db) == []


def test_owner_cannot_read_a_platforms_queue(client, practice_db):
    log_in_as(client, "test_owner", "owner")
    response = client.get("/api/queue?platform_id=901")
    assert response.status_code == 403
    assert "don't have access to the queue" in response.get_json()["error"]


def test_marshall_sees_only_his_platforms_queue(client, practice_db):
    conn = sqlite3.connect(practice_db)
    conn.execute("INSERT INTO queue (taxi_id, platform_id, layer, position, status) "
                 "VALUES (9002, 902, 'Test Layer', 1, 'waiting')")
    conn.commit()
    conn.close()
    log_in_as(client, "test_marshal_a", "marshall")
    join(client, 9001)
    response = client.get("/api/queue?platform_id=902")
    assert response.status_code == 200
    plates = [row["plate"] for row in response.get_json()]
    assert plates == ["OWN 001 GP"]