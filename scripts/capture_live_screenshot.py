import os
import time
from playwright.sync_api import sync_playwright
from PIL import Image

def capture_live():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            device_scale_factor=1.5
        )
        page = context.new_page()
        
        # Navigate to front view
        url = 'http://127.0.0.1:5173/?control=a'
        print(f"Navigating to {url}...")
        page.goto(url, wait_until='load', timeout=10000)
        
        # Wait 2 seconds for CSS animations, fonts, and images to settle
        page.wait_for_timeout(2000)
        
        out_path = r"c:\Users\dwinslow\Documents\Dexter_Controller_Project\docs\dexpad_hero_banner.png"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        page.screenshot(path=out_path)
        browser.close()
        
        im = Image.open(out_path)
        print(f"Captured live UI screenshot: {im.size} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    capture_live()
