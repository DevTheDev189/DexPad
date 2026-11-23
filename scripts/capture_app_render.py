import os
import sys
import time
import subprocess
import http.server
import socketserver
import threading
from PIL import Image, ImageStat

PORT = 5188
DIST_DIR = os.path.abspath('app/dist')
EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
OUTPUT_DIR = os.path.abspath('test_renders')
os.makedirs(OUTPUT_DIR, exist_ok=True)
SCREENSHOT_PATH = os.path.join(OUTPUT_DIR, 'app_full_render.png')
CROP_PATH = os.path.join(OUTPUT_DIR, 'controller_3d_crop.png')

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def run():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(('127.0.0.1', PORT), SilentHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    print(f"Local server started on http://127.0.0.1:{PORT}")
    time.sleep(1)

    temp_profile = os.path.join(os.environ.get('TEMP', os.getcwd()), 'edge_render_profile')
    os.makedirs(temp_profile, exist_ok=True)

    if os.path.exists(SCREENSHOT_PATH):
        os.remove(SCREENSHOT_PATH)

    cmd = [
        EDGE_PATH,
        '--headless=new',
        f'--user-data-dir={temp_profile}',
        '--enable-webgl',
        '--ignore-gpu-blocklist',
        '--window-size=1440,900',
        '--virtual-time-budget=6500',
        f'--screenshot={SCREENSHOT_PATH}',
        f'http://127.0.0.1:{PORT}/'
    ]

    print("Rendering WebGL scene with Headless Edge...")
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    print("Edge finished. Return code:", res.returncode)
    if res.stderr:
        print("Edge info:", res.stderr.strip()[:200])

    httpd.shutdown()

    if os.path.exists(SCREENSHOT_PATH):
        img = Image.open(SCREENSHOT_PATH)
        print(f"Captured screenshot: {img.size[0]}x{img.size[1]} ({img.format})")

        # Analyze overall image
        stat = ImageStat.Stat(img)
        print("Overall Mean RGB:", [round(x, 1) for x in stat.mean[:3]])

        # Crop the 3D Controller Viewport (Left pane)
        # On 1440x900, left pane is roughly x=28 to 720, y=70 to 820
        controller_crop = img.crop((32, 70, 720, 830))
        controller_crop.save(CROP_PATH)
        print(f"Saved 3D controller crop to {CROP_PATH} ({controller_crop.size[0]}x{controller_crop.size[1]})")

        crop_stat = ImageStat.Stat(controller_crop)
        print("Controller Viewport Mean RGB:", [round(x, 1) for x in crop_stat.mean[:3]])
        print("Controller Viewport Extrema (Min/Max):", crop_stat.extrema[:3])
        print("SUCCESS: 3D controller rendered and inspected with Pillow!")
    else:
        print("ERROR: Screenshot file was not created!")

if __name__ == '__main__':
    run()
