import sqlite3
from datetime import datetime, timedelta

def find_queue_integrity_issues(db_path, stale_hours=4, now=None):
    """
    Scans the queue for problems that shouldn't be possible but aren't
    actually prevented anywhere in the code. Returns a list of issues,
    each one flagged with WHAT is wrong -- never a guess at WHY, and
    never auto-corrected. A human decides what to do about each one.
    """
    now = now or datetime.now()   

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    issues = []

    cursor.execute("""
        SELECT taxi_id, COUNT(*) as waiting_count
        FROM queue
        WHERE status = 'waiting'
        GROUP BY taxi_id
        HAVING COUNT(*) > 1
    """)
    for row in cursor.fetchall():
        issues.append({
            "type": "DUPLICATE_QUEUE_ENTRY",
            "taxi_id": row["taxi_id"],
            "detail": f"Taxi {row['taxi_id']} has {row['waiting_count']} active 'waiting' "
                      f"queue rows at once -- should never be more than 1.",
        })

    cursor.execute("""
        SELECT q.id, q.taxi_id
        FROM queue q
        LEFT JOIN taxis t ON q.taxi_id = t.id
        WHERE q.status = 'waiting' AND t.id IS NULL
    """)
    for row in cursor.fetchall():
        issues.append({
            "type": "ORPHANED_QUEUE_ENTRY",
            "queue_id": row["id"],
            "taxi_id": row["taxi_id"],
            "detail": f"Queue row {row['id']} references taxi_id {row['taxi_id']}, "
                      f"which does not exist in the taxis table.",
        })

    cursor.execute("""
        SELECT q.id as queue_id, q.taxi_id, t.status as taxi_status
        FROM queue q
        JOIN taxis t ON q.taxi_id = t.id
        WHERE q.status = 'waiting' AND t.status != 'active'
    """)
    for row in cursor.fetchall():
        issues.append({
            "type": "INACTIVE_TAXI_IN_QUEUE",
            "queue_id": row["queue_id"],
            "taxi_id": row["taxi_id"],
            "details": f"Taxi {row['taxi_id']} is waiting in the queue, but its status "
                       f"is '{row['taxi_status']}', not 'active'.",
        })

    cutoff = (now - timedelta(hours=stale_hours)).strftime("%Y-%m-%d %H:%M:%S")   
    cursor.execute("""
        SELECT id, taxi_id, platform_id, joined_at
        FROM queue
        WHERE status = 'waiting' AND joined_at < ?
    """, (cutoff,))
    for row in cursor.fetchall():
        issues.append({
            "type": "STALE_QUEUE_ENTRY",
            "queue_id": row["id"],
            "taxi_id": row["taxi_id"],
            "detail": f"Taxi {row['taxi_id']} has been 'waiting' since {row['joined_at']} "
                      f"-- over {stale_hours}h ago, worth checking if it actually left.",
        })

    conn.close()
    return issues   


if __name__ == "__main__":
    DB_PATH = r"C:\Users\Sechaba\Desktop\python\taxi.db"
    issues = find_queue_integrity_issues(DB_PATH)

    if not issues:
        print("No queue integrity issues found.")
    else:
        print(f"Found {len(issues)} issue(s):\n")
        for issue in issues:
            print(f"- {issue['type']}: {issue['detail']}")