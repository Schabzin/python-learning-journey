from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
import datetime
import logging
from queue_integrity import find_queue_integrity_issues
from utils import get_db, login_required, get_weekend_letter, prdp_expiring_soon, get_db_path

logger = logging.getLogger(__name__)

marshall_bp = Blueprint("marshall", __name__)


@marshall_bp.route("/marshall")
@login_required
def marshall():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name FROM users u
        LEFT JOIN platforms p ON u.platform_id = p.id
        WHERE u.username = ?
    """, (session["user"],))
    result = cursor.fetchone()
    platform_name = result["name"] if result and result["name"] else "No platform assigned"
    today = datetime.date.today()
    days_until_saturday = (5 - today.weekday()) % 7
    upcoming_saturday = today + datetime.timedelta(days=days_until_saturday)
    current_letter = get_weekend_letter(upcoming_saturday)
    conn.close()
    return render_template("taxi_marshall.html", user=session["user"], platform_name=platform_name, current_letter=current_letter)

def validate_join_request(form):
    """
    Checks the raw form data for /api/queue/join BEFORE any database call.
    Returns (True, None) if valid, or (False, "reason") if not.
    """
    taxi_id = form.get("taxi_id")
    layer = form.get("layer")

    if not taxi_id:
        return False, "taxi_id is required"

    if not taxi_id.isdigit():
        return False, "taxi_id must be a number"

    if not layer or not layer.strip():
        return False, "layer is required"

    if len(layer) > 100:
        return False, "layer name is too long"

    return True, None

def validate_depart_request(form):
    """
    Checks the raw form data for /api/queue/depart BEFORE any database call.
    Returns (True, None) if valid, or (False, "reason") if not.
    """
    route_id = form.get("route_id")

    if not route_id or not route_id.strip():
        return False, "route_id is required"

    if len(route_id) > 100:
        return False, "route_id is too long"

    return True, None

def validate_remove_request(form):
    """
    Checks the raw form data for /api/queue/remove BEFORE any database call.
    Returns (True, None) if valid, or (False, "reason") if not --
    the caller decides what to do with the reason (flash message, JSON error, etc).
    """
    taxi_id = form.get("taxi_id")

    if not taxi_id:
        return False, "taxi_id is required"

    if not taxi_id.isdigit():
        return False, "taxi_id must be a number"

    return True, None

@marshall_bp.route("/api/queue/join", methods=["POST"])
@login_required
def join_queue():
    if session["role"] != "marshall":
        logger.warning("event=non_marshall_join_attempt user=%s", session["user"])
        return jsonify({"error": "Access denied"}), 403

    taxi_id = request.form.get("taxi_id")
    layer = request.form.get("layer")
    

    is_valid, error = validate_join_request(request.form)
    if not is_valid:
        return jsonify({"error": error}), 400

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("SELECT platform_id FROM users WHERE username = ?", (session["user"],))
        marshall_row = cursor.fetchone()
        platform_id = marshall_row["platform_id"]

        if not platform_id:
            logger.warning("event=marshall_no_platform user=%s", session["user"])
            conn.rollback()
            return jsonify({"error": error}), 500
        

        cursor.execute(
            "SELECT platform_id, layer, position FROM queue "
            "WHERE taxi_id = ? AND status = 'waiting'",
            (taxi_id,)
        )
        existing = cursor.fetchone()
        if existing is not None:
            conn.rollback()
            logger.warning(
                "event=duplicate_queue_join_blocked taxi_id=%s existing_platform=%s existing_layer=%s user=%s",
                taxi_id, existing["platform_id"], existing["layer"], session["user"]
            )
            return jsonify({
                "error": f"That taxi is already queued (platform {existing['platform_id']}, "
                         f"layer {existing['layer']}, position {existing['position']}). "
                         f"Remove it from that queue first."
            }), 409

        cursor.execute(
            "SELECT COALESCE(MAX(position), 0) as max_pos FROM queue WHERE platform_id = ? AND layer = ? AND status = 'waiting'",
            (platform_id, layer)
        )
        next_position = cursor.fetchone()["max_pos"] + 1

        cursor.execute("""
            INSERT INTO queue (taxi_id, platform_id, layer, position, status)
            VALUES (?, ?, ?, ?, 'waiting')
        """, (taxi_id, platform_id, layer, next_position))
        conn.commit()
        return jsonify({"message": f"Taxi added to queue at position {next_position}"}), 200
    except Exception:
        conn.rollback()
        logger.exception("event=join_queue_failed user=%s", session["user"])
        return jsonify({"error": "Could not process queue join"}), 500
    finally:
        conn.close()


@marshall_bp.route("/api/queue/depart", methods=["POST"])
@login_required
def depart_queue():
    if session["role"] != "marshall":
        logger.warning("event=non_marshall_depart_queue_attempt user=%s", session["user"])
        return jsonify({"error": "Access denied"}), 403

    route_id = request.form.get("route_id")
    if not route_id:
        return jsonify({"error": "Route is required"}), 400

    is_valid, error = validate_depart_request(request.form)
    if not is_valid:
        return jsonify({"error": error}), 400

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("SELECT platform_id FROM users WHERE username = ?", (session["user"],))
        platform_id = cursor.fetchone()["platform_id"]

        cursor.execute("""
            SELECT id, taxi_id, layer FROM queue WHERE platform_id = ? AND status = 'waiting'
            ORDER BY position ASC LIMIT 1
        """, (platform_id,))
        front = cursor.fetchone()

        if not front:
            logger.info("event=depart_empty_queue user=%s platform_id=%s", session["user"], platform_id)
            conn.rollback()
            return jsonify({"error": "Queue is empty"}), 400
        cursor.execute(
            "UPDATE queue SET status = 'departed' WHERE id = ? AND status = 'waiting'",
            (front["id"],)
        )

        if cursor.rowcount == 0:
            logger.warning("event=depart_race_detected user=%s queue_id=%s", session["user"], front["id"])
            conn.rollback()
            return jsonify({"error": "Taxi already departed by another marshall"}), 409

        cursor.execute(
            "INSERT INTO trips (taxi_id, route_id, logged_by) VALUES (?, ?, ?)",
            (front["taxi_id"], route_id, session["user_id"])
        )

        cursor.execute(
            "UPDATE queue SET position = position - 1 WHERE platform_id = ? AND layer = ? AND status = 'waiting'",
            (platform_id, front["layer"])
        )
        conn.commit()
        logger.info("event=depart_success user=%s platform_id=%s taxi_id=%s",
                    
                    session["user"], platform_id, front["taxi_id"])
        
        return jsonify({"message": "Trip logged, position 1 departed, queue shifted"}), 200

    except Exception:
        conn.rollback()
        logger.exception("event=depart_queue_failed user=%s", session["user"])
        
        return jsonify({"error": "Could not process departure"}), 500
    finally:
        conn.close()

@marshall_bp.route("/api/queue/remove", methods=["POST"])
@login_required
def remove_from_queue():
    if session["role"] != "marshall":
        logger.warning("event=non_marshall_remove_attempt user=%s", session["user"])
        return jsonify({"error": "Access denied"}), 403

    taxi_id = request.form.get("taxi_id")
    if not taxi_id:
        return jsonify({"error": "taxi_id is required"}), 400

    is_valid, error = validate_remove_request(request.form)
    if not is_valid:
        return jsonify({"error": error}), 400

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("SELECT platform_id FROM users WHERE username = ?", (session["user"],))
        marshall_platform_id = cursor.fetchone()["platform_id"]

        cursor.execute(
            "SELECT id, platform_id, layer, position FROM queue "
            "WHERE taxi_id = ? AND status = 'waiting'",
            (taxi_id,)
        )
        row = cursor.fetchone()

        if row is None:
            conn.rollback()
            return jsonify({"error": "That taxi is queued at a different platform"}), 404

        cursor.execute(
            "UPDATE queue SET status = 'removed' WHERE id = ? AND status = 'waiting'",
            (row["id"],)
        )
        if cursor.rowcount == 0:
            logger.warning("event=remove_race_detected user=%s queue_id=%s", session["user"], row["id"])
            conn.rollback()
            return jsonify({"error": "Taxi's queue status already changed"}), 409

        cursor.execute(
            "UPDATE queue SET position = position - 1 "
            "WHERE platform_id = ? AND layer = ? AND status = 'waiting' AND position > ?",
            (row["platform_id"], row["layer"], row["position"])
        )

        conn.commit()
        logger.info("event=remove_success user=%s taxi_id=%s platform_id=%s layer=%s",
                    session["user"], taxi_id, row["platform_id"], row["layer"])
        return jsonify({"message": f"Taxi removed from queue, {row['layer']} shifted"}), 200
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

@marshall_bp.route("/api/queue", methods=["GET"])
@login_required
def get_queue():
    conn = get_db()
    cursor = conn.cursor()

    if session["role"] == "marshall":
        cursor.execute("SELECT platform_id FROM users WHERE username = ?", (session["user"],))
        platform_id = cursor.fetchone()["platform_id"]
    elif session["role"] == "driver":
        cursor.execute("SELECT platform_id FROM taxis WHERE driver_username = ?", (session["user"],))
        taxi_row = cursor.fetchone()
        platform_id = taxi_row["platform_id"] if taxi_row else None
    else:
        platform_id = request.args.get("platform_id")

    cursor.execute("""
        SELECT q.id, q.position, q.status, q.layer, t.plate, t.driver_name
        FROM queue q
        JOIN taxis t ON q.taxi_id = t.id
        WHERE q.platform_id = ? AND q.status = 'waiting'
        ORDER BY q.position ASC
    """, (platform_id,))
    queue = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(queue)

@marshall_bp.route("/api/queue/issues", methods=["GET"])
@login_required
def queue_issues():
    """Read-only. Surfaces whatever find_queue_integrity_issues() catches,
    through the app -- no terminal, no manual script, no remembering."""
    if session["role"] != "marshall":
        return jsonify({"error": "Access denied"}), 403

    issues = find_queue_integrity_issues(get_db_path())
    return jsonify({
        "issue_count": len(issues),
        "issues": issues,
    }), 200


@marshall_bp.route("/api/layers")
@login_required
def get_layers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT platform_id FROM users WHERE username = ?", (session["user"],))
    platform_id = cursor.fetchone()["platform_id"]
    cursor.execute("SELECT id, name FROM layers WHERE platform_id = ?", (platform_id,))
    layers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(layers)


@marshall_bp.route("/api/taxis", methods=["GET"])
@login_required
def get_taxis():
    today = datetime.date.today().isoformat()
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    if session["role"] == "marshall":
        cursor.execute("""
            SELECT t.id, t.plate, t.driver_name, t.status, t.current_km, t.next_service_km, t.prdp_expiry,
                    COUNT(tr.id) as trips_today,
                    COALESCE(dt.target_amount, 750) as target,
                    COALESCE(dt.collected_amount, 0) as collected
            FROM taxis t
            LEFT JOIN trips tr ON t.id = tr.taxi_id AND DATE(tr.timestamp) = ?
            LEFT JOIN daily_targets dt ON t.id = dt.taxi_id AND dt.date = ?
            GROUP BY t.id
        """, (today, today))
    else:
        cursor.execute("""
            SELECT t.id, t.plate, t.driver_name, t.status, t.current_km, t.next_service_km, t.prdp_expiry,
                    COUNT(tr.id) as trips_today,
                    COALESCE(dt.target_amount, 750) as target,
                    COALESCE(dt.collected_amount, 0) as collected
            FROM taxis t
            LEFT JOIN trips tr ON t.id = tr.taxi_id AND DATE(tr.timestamp) = ?
            LEFT JOIN daily_targets dt ON t.id = dt.taxi_id AND dt.date = ?
            WHERE t.owner_id = ?
            GROUP BY t.id
        """, (today, today, session["user_id"]))
    taxis = [dict(row) for row in cursor.fetchall()]

    for taxi in taxis:
        cursor.execute("""
            SELECT COUNT(tr.id) as week_trips, COALESCE(SUM(dt.collected_amount), 0) as week_collected
            FROM trips tr
            LEFT JOIN daily_targets dt ON tr.taxi_id = dt.taxi_id AND dt.date = DATE(tr.timestamp)
            WHERE tr.taxi_id = ? AND DATE(tr.timestamp) >= ?
        """, (taxi["id"], week_ago))
        taxi_week = cursor.fetchone()
        taxi["week_trips"] = taxi_week["week_trips"]
        taxi["week_collected"] = taxi_week["week_collected"]

        if prdp_expiring_soon(taxi.get("prdp_expiry")):
            taxi["prdp_warning"] = f"PrDP expires {taxi['prdp_expiry']} - renew soon"
        elif taxi.get("prdp_expiry") and datetime.datetime.strptime(taxi["prdp_expiry"], "%Y-%m-%d").date() < datetime.date.today():
                    taxi["prdp_warning"] = f"PrDP EXPIRED on {taxi['prdp_expiry']} - this is urgent"

    conn.close()
    return jsonify(taxis)


@marshall_bp.route("/api/routes", methods=["GET"])
@login_required
def get_routes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes")
    routes = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(routes)