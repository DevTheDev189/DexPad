import os
import sys
import time
import subprocess
import http.server
import socketserver
import threading
from PIL import Image, ImageStat

PORT = 5211
DIST_DIR = os.path.abspath('app/dist')
EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
OUTPUT_DIR = os.path.abspath('test_renders_v2')
os.makedirs(OUTPUT_DIR, exist_ok=True)

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

print("Starting server...", flush=True)
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(('127.0.0.1', PORT), SilentHandler)
server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
server_thread.start()
print(f"Local server started on http://127.0.0.1:{PORT}", flush=True)

temp_profile = os.path.join(os.environ.get('TEMP', os.getcwd()), 'edge_render_profile_v3')
os.makedirs(temp_profile, exist_ok=True)

out_full = os.path.join(OUTPUT_DIR, "test_front.png")
cmd = [
    EDGE_PATH,
    '--headless=new',
    f'--user-data-dir={temp_profile}',
    '--no-sandbox',
    '--enable-webgl',
    '--ignore-gpu-blocklist',
    '--window-size=1440,900',
    '--virtual-time-budget=5000',
    f'--screenshot={out_full}',
    f'http://127.0.0.1:{PORT}/?finish=galaxy&angle=front&control=a'
]

print("Executing Edge...", flush=True)
res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
print(f"Edge exited with code {res.returncode}", flush=True)
if os.path.exists(out_full):
    img = Image.open(out_full)
    print(f"Image saved! Dimensions: {img.size}", flush=True)
else:
    print("Screenshot not created! stderr:", res.stderr, flush=True)

httpd.shutdown()
