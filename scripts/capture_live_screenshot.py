import os
import time
from playwright.sync_api import sync_playwright
from PIL import Image

def capture_live():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 1440x900 viewport with device_scale_factor=1.5 for high-DPI clarity without excessive file size
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            device_scale_factor=1.5
        )
        page = context.new_page()
        
        # Navigate with pre-selected control to show glowing hotspot and mapping row
        url = 'http://127.0.0.1:5173/?control=r2'
        print(f"Navigating to {url}...")
        page.goto(url, wait_until='networkidle', timeout=15000)
        
        # Give ambient animations, controller render, and fonts 2.5 seconds to settle
        time.sleep(2.5)
        
        out_path = r"c:\Users\dwinslow\Documents\Dexter_Controller_Project\docs\dexpad_hero_banner.png"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        page.screenshot(path=out_path)
        browser.close()
        
        # Check size
        im = Image.open(out_path)
        print(f"Captured live UI screenshot: {im.size} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    capture_live()
