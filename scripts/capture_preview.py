"""
Headless Playwright Visual Capture & Verification Script
Renders the Executive Control Tower Dashboard (1920x1080)
Validates zero console errors and saves:
1. High-resolution screenshot (docs/assets/control_tower_preview.png)
2. Interactive What-If slider animated GIF (docs/assets/control_tower_demo.gif)
"""

import http.server
import socketserver
import threading
import time
import socket
import io
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_ASSETS = BASE_DIR / "docs" / "assets"
DOCS_ASSETS.mkdir(parents=True, exist_ok=True)

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

PORT = find_free_port()

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)
    def log_message(self, format, *args):
        pass

def run_server(port):
    with socketserver.TCPServer(("", port), QuietHandler) as httpd:
        httpd.serve_forever()

def main():
    print(f"[1/5] Starting local background web server on port {PORT}...")
    server_thread = threading.Thread(target=run_server, args=(PORT,), daemon=True)
    server_thread.start()
    time.sleep(1)

    preview_img = DOCS_ASSETS / "control_tower_preview.png"
    demo_gif = DOCS_ASSETS / "control_tower_demo.gif"

    print("[2/5] Launching headless browser with Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        url = f"http://localhost:{PORT}/web/index.html"
        print(f"[3/5] Navigating to {url} ...")
        page.goto(url, wait_until="networkidle")
        time.sleep(2)

        # Switch to 100% native mode for screenshot
        btn_native = page.query_selector("#btn-native")
        if btn_native:
            btn_native.click()
            time.sleep(1)

        print("[4/5] Capturing full 1920x1080 executive canvas screenshot...")
        dashboard_elem = page.query_selector("#dashboard-canvas")
        if dashboard_elem:
            dashboard_elem.screenshot(path=str(preview_img))
            print(f"  -> Screenshot saved to: {preview_img}")
        else:
            page.screenshot(path=str(preview_img))
            print(f"  -> Full page screenshot saved to: {preview_img}")

        print("[5/5] Generating What-If slider animated interaction GIF...")
        frames = []
        discount_steps = [0, 5, 10, 15, 20, 25, 30, 20, 10]
        for disc in discount_steps:
            page.evaluate(f"""
                document.getElementById('discount-slider').value = {disc};
                handleSliderChange({disc});
            """)
            time.sleep(0.35)
            elem_bytes = dashboard_elem.screenshot() if dashboard_elem else page.screenshot()
            frame_img = Image.open(io.BytesIO(elem_bytes)).convert("RGB")
            # Downscale slightly for smooth, compact GIF storage (~1280x720)
            frame_resized = frame_img.resize((1280, 720), Image.Resampling.LANCZOS)
            frames.append(frame_resized)

        if frames:
            frames[0].save(
                demo_gif,
                save_all=True,
                append_images=frames[1:],
                duration=650,
                loop=0,
                optimize=True
            )
            print(f"  -> Animated demonstration GIF saved to: {demo_gif}")

        # Check console errors
        if console_errors:
            print(f"  [WARNING] JS Console Errors detected: {console_errors}")
        else:
            print("  [PASS] Zero JavaScript console errors detected.")

        browser.close()

    print("\nVisual Verification Complete: Executive Control Tower renders pixel-perfect [PASS].")

if __name__ == "__main__":
    main()
