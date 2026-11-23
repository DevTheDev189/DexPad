import os
import sys
import time
import subprocess
import http.server
import socketserver
import threading
from PIL import Image

PORT = 5244
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
print("Server ready on", PORT, flush=True)

out = os.path.join(OUTPUT_DIR, 'fast_test.png')
user_data = os.path.join(os.environ.get('TEMP', os.getcwd()), 'fast_edge_user')
os.makedirs(user_data, exist_ok=True)

# Edge command WITHOUT virtual-time-budget
cmd = [
    EDGE_PATH,
    '--headless=new',
    f'--user-data-dir={user_data}',
    '--enable-webgl',
    '--ignore-gpu-blocklist',
    '--window-size=1440,900',
    f'--screenshot={out}',
    f'http://127.0.0.1:{PORT}/?finish=galaxy&angle=front'
]

print("Starting Edge...", flush=True)
t0 = time.time()
res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
t1 = time.time()
print(f"Done in {t1 - t0:.2f}s! Exit code: {res.returncode}", flush=True)
if os.path.exists(out):
    print("Screenshot exists! Size:", os.path.getsize(out), flush=True)
    im = Image.open(out)
    print("Image size:", im.size, flush=True)
else:
    print("Screenshot missing! Stderr:", res.stderr, flush=True)

httpd.shutdown()
