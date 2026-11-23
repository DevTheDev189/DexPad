import os
import sys
import time
import subprocess
import http.server
import socketserver
import threading
from PIL import Image, ImageStat

PORT = 5199
DIST_DIR = os.path.join(os.getcwd(), 'app', 'dist')
EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
OUTPUT_DIR = os.path.join(os.getcwd(), 'test_renders')
os.makedirs(OUTPUT_DIR, exist_ok=True)
SCREENSHOT_PATH = os.path.join(OUTPUT_DIR, 'render_preview.png')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)
    def log_message(self, format, *args):
        pass # Suppress logging

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
        httpd.serve_forever()

# Start HTTP server in background thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
print(f"HTTP Server serving {DIST_DIR} on http://127.0.0.1:{PORT}")
time.sleep(1)

# Run Headless Edge with WebGL enabled
cmd = [
    EDGE_PATH,
    '--headless=new',
    '--enable-webgl',
    '--use-gl=angle',
    '--use-angle=d3d11',
    '--ignore-gpu-blocklist',
    '--window-size=1440,900',
    '--run-all-compositor-stages-before-draw',
    '--virtual-time-budget=6000', # Allow 6 seconds for WebGL & GLTF loading
    f'--screenshot={SCREENSHOT_PATH}',
    f'http://127.0.0.1:{PORT}'
]

print("Launching Headless Edge to capture WebGL render...")
proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25)
print("Edge finished with code:", proc.returncode)

if os.path.exists(SCREENSHOT_PATH):
    img = Image.open(SCREENSHOT_PATH)
    print(f"Screenshot successfully captured: {img.size[0]}x{img.size[1]} pixels ({img.format})")
    
    # Analyze image with Pillow
    stat = ImageStat.Stat(img)
    print("Mean RGB channels:", [round(x, 2) for x in stat.mean[:3]])
    print("Band min/max:", img.getextrema()[:3])
    
    # Crop central 3D viewport region to analyze controller render
    # Viewport is left pane roughly: x=28 to 720, y=70 to 760
    viewport_crop = img.crop((40, 80, 720, 760))
    crop_path = os.path.join(OUTPUT_DIR, 'viewport_crop.png')
    viewport_crop.save(crop_path)
    
    crop_stat = ImageStat.Stat(viewport_crop)
    print("Viewport Mean RGB:", [round(x, 2) for x in crop_stat.mean[:3]])
    print("Viewport Max brightness:", [x[1] for x in crop_stat.extrema[:3]])
    print(f"Saved viewport crop to {crop_path}")
else:
    print("Screenshot failed to generate!")
