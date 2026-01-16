
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def capture_screenshots(output_dir: str, username: str = None, password: str = None, base_url: str = "http://localhost:8501"):
    """
    Launch browser, log in (if credentials provided), and capture screenshots of main pages.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        print(f"Navigating to {base_url}...")
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        
        # Check for login
        if "GEO Tool – 登录" in page.title() or page.locator("input[type='password']").count() > 0:
            print("Login page detected.")
            if username and password:
                print("Attempting login...")
                # Streamlit input fields usually have aria-label or accessible names
                # We try to target by label text if possible, or order
                page.locator("input[type='text']").first.fill(username) # Username
                page.locator("input[type='password']").first.fill(password) # Password
                page.get_by_text("登录", exact=True).click()
                page.wait_for_load_state("networkidle")
                time.sleep(2) # Wait for potential redirect/reload
            else:
                print("No credentials provided. Capturing login page only.")
        
        # Capture Dashboard
        page.screenshot(path=str(output_path / "1_dashboard.png"))
        print("Captured dashboard.")
        
        # Navigate to "运行流水线" (Run Pipeline)
        # Click sidebar radio button. Streamlit radios are tricky.
        # usually text match works.
        try:
            page.get_by_text("运行流水线").click()
            time.sleep(2)
            page.screenshot(path=str(output_path / "2_pipeline.png"))
            print("Captured pipeline page.")
            
            page.get_by_text("压力测试").click()
            time.sleep(2)
            page.screenshot(path=str(output_path / "3_pressure_test.png"))
            print("Captured pressure test page.")
            
            page.get_by_text("对比报告").click()
            time.sleep(2)
            page.screenshot(path=str(output_path / "4_comparison.png"))
            print("Captured comparison page.")
            
        except Exception as e:
            print(f"Navigation error: {e}")
        
        browser.close()
        
    return str(output_path)

if __name__ == "__main__":
    import sys
    out_dir = "output/screenshots"
    user = sys.argv[1] if len(sys.argv) > 1 else None
    pw = sys.argv[2] if len(sys.argv) > 2 else None
    
    capture_screenshots(out_dir, user, pw)
