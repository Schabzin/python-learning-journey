import importlib
import sys
import os

import pytest

from utils import get_db  

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)


def _fresh_app():
    """(Re)import taxi_app.py and setup_taxi_db.py from scratch, against
    whatever the CURRENT working directory is. Must only be called AFTER
    chdir'ing into an isolated tmp folder -- otherwise this touches the
    real taxi.db."""
    for name in ("setup_taxi_db", "taxi_app"):
        if name in sys.modules:
            importlib.reload(sys.modules[name])
        else:
            importlib.import_module(name)
    return sys.modules["taxi_app"]


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  
    app_module = _fresh_app()
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO platforms (name, rank_name) VALUES (?, ?)",
            ("Platform 1", "Evaton Rank")
        )
        platform_id = cursor.lastrowid
        cursor.execute(
            "UPDATE users SET platform_id = ? WHERE username = ?",
            (platform_id, "marshall1")
        )
        conn.commit()
        conn.close()

        with client.session_transaction() as sess:
            sess["user"] = "marshall1"
            sess["role"] = "marshall"
        yield client


def join(client, taxi_id, layer):
    return client.post("/api/queue/join", data={"taxi_id": taxi_id, "layer": layer})


def test_duplicate_queue_join_is_blocked(client):
    first = join(client, taxi_id="101", layer="Zone 3 via Residensia")
    assert first.status_code == 200

    second = join(client, taxi_id="101", layer="Zone 3 via Residensia")
    assert second.status_code in (302, 303)  

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM queue WHERE taxi_id = ? AND status = 'waiting'", (101,)
    ).fetchall()
    conn.close()
    assert len(rows) == 1
    assert rows[0]["position"] == 1  


def test_duplicate_join_blocked_even_on_a_different_layer(client):
    join(client, taxi_id="102", layer="Zone 3 via Residensia")
    join(client, taxi_id="102", layer="Eastern road")

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM queue WHERE taxi_id = ? AND status = 'waiting'", (102,)
    ).fetchall()
    conn.close()
    assert len(rows) == 1
    assert rows[0]["layer"] == "Zone 3 via Residensia"  


def test_taxi_can_rejoin_after_leaving_queue(client):
    join(client, taxi_id="103", layer="Zone 3 via Residensia")

    conn = get_db()
    conn.execute(
        "UPDATE queue SET status = 'departed' WHERE taxi_id = ? AND status = 'waiting'",
        (103,)
    )
    conn.commit()
    conn.close()

    second = join(client, taxi_id="103", layer="Eastern road")
    assert second.status_code == 200

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM queue WHERE taxi_id = ? AND status = 'waiting'", (103,)
    ).fetchall()
    conn.close()
    assert len(rows) == 1
    assert rows[0]["layer"] == "Eastern road"