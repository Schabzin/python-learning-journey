from playwright.sync_api import sync_playwright

def test_dashboard_shows_prdp_warning_after_js_runs():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:5000/login")
        page.fill('input[name="username"]', "chahane")
        page.fill('input[name="password"]', "kalikeng2026")
        page.click('button[type="submit"]')
        page.goto("http://127.0.0.1:5000/dashboard")
        page.wait_for_timeout(1000)
        content = page.content()
        assert "PrDP EXPIRED" in content
        browser.close()
        print("Test passed -- PrDP warning genuinely visible on rendered page")

test_dashboard_shows_prdp_warning_after_js_runs()