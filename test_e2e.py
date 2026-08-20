import pytest
import sqlite3
import bcrypt
import datetime
from playwright.sync_api import Page, expect

def setup_prdp_test_data():
    conn = sqlite3.connect("taxi.db")
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(b"kalikeng2026", bcrypt.gensalt())
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('chahane', ?, 'owner')", (hashed,))
    cursor.execute("SELECT id FROM users WHERE username = 'chahane'")
    owner_id = cursor.fetchone()[0]
    past_date = (datetime.date.today() - datetime.timedelta(days=10)).isoformat()
    cursor.execute("""
        INSERT OR IGNORE INTO taxis (plate, driver_name, driver_username, owner_id, prdp_expiry)
        VALUES ('E2ETEST GP', 'Test Driver', 'e2etestdriver', ?, ?)
    """, (owner_id, past_date))
    conn.commit()
    conn.close()

def login_as(page: Page, username: str, password: str):
    page.goto("http://127.0.0.1:5000/login")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')

def test_dashboard_shows_prdp_warning(page: Page):
    setup_prdp_test_data()
    login_as(page, "chahane", "kalikeng2026")
    page.goto("http://127.0.0.1:5000/dashboard")
    page.wait_for_timeout(1000)
    expect(page.locator("body")).to_contain_text("PrDP EXPIRED")

def test_marshall_can_join_and_depart_queue(page: Page):
    login_as(page, "marshall1", "marshall123")
    page.goto("http://127.0.0.1:5000/marshall")
    page.select_option("#taxi-select", label="TEST01 GP - Shane")
    page.select_option("#layer-select", label="Straight Evaton")
    page.click("#join-queue-btn")
    page.wait_for_timeout(500)
    expect(page.locator("#message")).to_contain_text("added to queue at position")
        