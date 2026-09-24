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

def remove(client, taxi_id):
    return client.post("/api/queue/remove", data={"taxi_id": taxi_id})

def test_removing_middle_taxi_shifts_only_those_behind_it(client):
    join(client, taxi_id="101", layer="Zone 3 via Residensia")
    join(client, taxi_id="102", layer="Zone 3 via Residensia")
    join(client, taxi_id="103", layer="Zone 3 via Residensia")

    response = remove(client, taxi_id="102")
    assert response.status_code == 200

    conn = get_db()
    row_103 = conn.execute(
        "SELECT position FROM queue WHERE taxi_id = ? AND status = 'waiting'", (103,)
    ).fetchone()
    conn.close()
    assert row_103["position"] == 2

    conn = get_db()
    row_102 = conn.execute(
        "SELECT * FROM queue WHERE taxi_id = ? AND status = 'waiting'", (102,)
    ).fetchone()
    conn.close()
    assert row_102 is None

def test_removing_from_one_layer_does_not_shift_another_layer(client):
    join(client, taxi_id="201", layer="Zone 3 via Residensia")
    join(client, taxi_id="202", layer="Zone 3 via Residensia")
    join(client, taxi_id="301", layer="Eastern road")

    remove(client, taxi_id="201")

    conn = get_db()
    row_202 = conn.execute(
        "SELECT position FROM queue WHERE taxi_id = ? AND status = 'waiting'", (202,)
    ).fetchone()
    conn.close()
    assert row_202["position"] == 1

    conn = get_db()
    row_301 = conn.execute(
        "SELECT position FROM queue WHERE taxi_id = ? AND status = 'waiting'", (301,)
    ).fetchone()
    conn.close()
    assert row_301["position"] == 1
                       