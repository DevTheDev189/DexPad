import os
import sys
import time
import subprocess
import http.server
import socketserver
import threading
from PIL import Image

PORT = 5255
DIST_DIR = os.path.abspath('app/dist')
EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
OUTPUT_DIR = os.path.abspath('test_renders_fast')
os.makedirs(OUTPUT_DIR, exist_ok=True)

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

httpd = socketserver.TCPServer(('127.0.0.1', PORT), SilentHandler)
server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
server_thread.start()

out = os.path.join(OUTPUT_DIR, 'test_flags.png')
user_data = os.path.join(os.environ.get('TEMP', os.getcwd()), 'edge_flags_profile')
os.makedirs(user_data, exist_ok=True)

cmd = [
    EDGE_PATH,
    '--headless=new',
    f'--user-data-dir={user_data}',
    '--no-sandbox',
    '--disable-gpu-sandbox',
    '--disable-features=WebUSB,WebHID,UsbDevice,OptimizationGuideModelDownloading',
    '--disable-device-discovery-notifications',
    '--enable-webgl',
    '--ignore-gpu-blocklist',
    '--window-size=1440,900',
    '--virtual-time-budget=3500',
    f'--screenshot={out}',
    f'http://127.0.0.1:{PORT}/?finish=galaxy&angle=front'
]

print("Starting Edge with flags...", flush=True)
res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
print(f"Exit code: {res.returncode}", flush=True)
if os.path.exists(out):
    print("Screenshot success! File size:", os.path.getsize(out), flush=True)
    im = Image.open(out)
    print("Image size:", im.size, flush=True)
else:
    print("Missing screenshot. Stderr:", res.stderr[:300], flush=True)

httpd.shutdown()
