"""
test_checkpoints.py -- proves every rule in checkpoints.py holds.
Each test gets its own throwaway database; the real taxi.db is never touched.
"""

import sqlite3
import pytest
from checkpoints import CheckpointChainError, get_checkpoint_chain, set_checkpoint_chain

@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test_checkpoints.db"
    conn = sqlite3.connect(path)
    try:
        conn.executescript("""
            CREATE TABLE routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                fare_per_passenger REAL NOT NULL DEFAULT 0
            );
            
            CREATE TABLE geofence_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                zone_type TEXT NOT NULL CHECK (zone_type IN ('rank', 'destination', 'checkpoint')),
                center_lat REAL NOT NULL,
                center_lon REAL NOT NULL,
                radius_meters REAL NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE route_checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER NOT NULL,
                zone_id INTEGER NOT NULL,
                sequence INTEGER NOT NULL CHECK (sequence >= 1),
                boarding_fare REAL CHECK (boarding_fare IS NULL OR boarding_fare > 0),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes(id),
                FOREIGN KEY (zone_id) REFERENCES geofence_zones(id),
                UNIQUE (route_id, sequence),
                UNIQUE (route_id, zone_id)
            );

            INSERT INTO routes (id, name, fare_per_passenger) VALUES
                (1, 'Sebokeng - Vanderbijlpark', 24),
                (2, 'Fare Not Set', 0);

            -- test-only placeholder coordinates, not real gate locations
            INSERT INTO geofence_zones (id, name, zone_type, center_lat, center_lon, radius_meters, active) VALUES
                (10, 'Sebokeng Rank',    'rank',       -26.60, 27.85, 80, 1),
                (11, 'After R54',        'checkpoint', -26.62, 27.80, 80, 1),
                (12, 'After Boipatong',  'checkpoint', -26.66, 27.82, 80, 1),
                (13, 'After Licence',    'checkpoint', -26.70, 27.83, 80, 1),
                (14, 'Old Gate',         'checkpoint', -26.65, 27.81, 80, 0);

        """)
        conn.commit()
    finally:
        conn.close()
    return str(path)

GOOD_CHAIN = [
    {"zone_id": 11, "boarding_fare": 18},
    {"zone_id": 12, "boarding_fare": 15},
    {"zone_id": 13, "boarding_fare": None},
]

def test_chain_is_saved_in_route_order_with_fares(db_path):
    chain = set_checkpoint_chain(1, GOOD_CHAIN, db_path=db_path)

    assert chain["full_fare"] == 24
    assert [g["zone_id"] for g in chain["gates"]] == [11, 12, 13]
    assert [g["sequence"] for g in chain["gates"]] == [1, 2, 3]
    assert [g["boarding_fare"] for g in chain["gates"]] == [18, 15, None]

def test_no_boarding_expected_is_stored_as_none_not_zero(db_path):
    chain = set_checkpoint_chain(1, GOOD_CHAIN, db_path=db_path)

    last_gate = chain["gates"][-1]
    assert last_gate["boarding_fare"] is None

def test_route_without_chain_returns_empty_gates_but_full_fare(db_path):
    chain = get_checkpoint_chain(1, db_path=db_path)

    assert chain["gates"] == []
    assert chain["full_fare"] == 24

def test_setting_a_chain_again_replaces_the_old_one(db_path):
    set_checkpoint_chain(1, GOOD_CHAIN, db_path=db_path)
    chain = set_checkpoint_chain(
        1,
        [{"zone_id": 11, "boarding_fare": 18}, {"zone_id": 13, "boarding_fare": None}],
        db_path=db_path,
    )

    assert [g["zone_id"] for g in chain["gates"]] == [11, 13]
    assert [g["sequence"] for g in chain["gates"]] == [1, 2]

def test_rejects_fewer_than_two_gates(db_path):
    with pytest.raises(CheckpointChainError, match="at least 2 gates"):
        set_checkpoint_chain(1, [{"zone_id": 11, "boarding_fare": 18}], db_path=db_path)

def test_rejects_duplicate_zone(db_path):
    gates = [{"zone_id": 11, "boarding_fare": 18}, {"zone_id": 11, "boarding_fare": 15}]
    with pytest.raises(CheckpointChainError, match="only appear once"):
        set_checkpoint_chain(1, gates, db_path=db_path)

def test_rejects_unknown_zone(db_path):
    gates = [{"zone_id": 11, "boarding_fare": 18}, {"zone_id": 999, "boarding_fare": None}]
    with pytest.raises(CheckpointChainError, match="do not exist"):
        set_checkpoint_chain(1, gates, db_path=db_path)

def test_rejects_deactivated_zone(db_path):
    gates = [{"zone_id": 11, "boarding_fare": 18}, {"zone_id": 14, "boarding_fare": None}]
    with pytest.raises(CheckpointChainError, match="deactivated"):
        set_checkpoint_chain(1, gates, db_path=db_path)

def test_rejects_rank_used_as_gate(db_path):
    gates = [{"zone_id": 10, "boarding_fare": 18}, {"zone_id": 11, "boarding_fare": None}]
    with pytest.raises(CheckpointChainError, match="'checkpoint' zones"):
        set_checkpoint_chain(1, gates, db_path=db_path)

def test_rejects_unknown_route(db_path):
    with pytest.raises(CheckpointChainError, match="does not exist"):
        set_checkpoint_chain(999, GOOD_CHAIN, db_path=db_path)

def test_rejects_route_without_full_fare(db_path):
    with pytest.raises(CheckpointChainError, match="no full fare set"):
        set_checkpoint_chain(2, GOOD_CHAIN, db_path=db_path)

@pytest.mark.parametrize("bad_fare", [0, -5, True, float("inf")])
def test_rejects_invalid_fare(db_path, bad_fare):
    gates = [{"zone_id": 11, "boarding_fare": bad_fare}, {"zone_id": 12, "boarding_fare": None}]
    with pytest.raises(CheckpointChainError, match="boarding_fare must be None"):
        set_checkpoint_chain(1, gates, db_path=db_path)

def test_failed_replace_leaves_old_chain_untouched(db_path):
    set_checkpoint_chain(1, GOOD_CHAIN, db_path=db_path)

    bad = [{"zone_id": 11, "boarding_fare": 18}, {"zone_id": 14, "boarding_fare": None}]
    with pytest.raises(CheckpointChainError):
        set_checkpoint_chain(1, bad, db_path=db_path)

    chain = get_checkpoint_chain(1, db_path=db_path)
    assert [g["zone_id"] for g in chain["gates"]] == [11, 12, 13]