import os
import sys
import time
import subprocess
import http.server
import socketserver
import threading
from PIL import Image, ImageStat

PORT = 5199
DIST_DIR = os.path.abspath('app/dist')
EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
OUTPUT_DIR = os.path.abspath('test_renders_v2')
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

    temp_profile = os.path.join(os.environ.get('TEMP', os.getcwd()), 'edge_render_profile_v2')
    os.makedirs(temp_profile, exist_ok=True)

    configs = [
        ('front_galaxy_overview', 'finish=galaxy&angle=front'),
        ('front_galaxy_button_a', 'finish=galaxy&angle=front&control=a'),
        ('front_galaxy_dpad_up', 'finish=galaxy&angle=front&control=dpad_up'),
        ('top_galaxy_triggers', 'finish=galaxy&angle=top&control=l1'),
        ('iso_galaxy_showcase', 'finish=galaxy&angle=iso'),
    ]

    for name, query in configs:
        out_full = os.path.join(OUTPUT_DIR, f"{name}_full.png")
        out_crop = os.path.join(OUTPUT_DIR, f"{name}_crop.png")

        cmd = [
            EDGE_PATH,
            '--headless=new',
            f'--user-data-dir={temp_profile}',
            '--enable-webgl',
            '--ignore-gpu-blocklist',
            '--window-size=1440,900',
            '--virtual-time-budget=6500',
            f'--screenshot={out_full}',
            f'http://127.0.0.1:{PORT}/?{query}'
        ]

        print(f"Rendering {name} ({query})...")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        except Exception as e:
            print(f"Subprocess error: {e}")
            continue

        if os.path.exists(out_full):
            img = Image.open(out_full)
            # Crop 3D stage area (left side of the app)
            crop = img.crop((32, 70, 720, 830))
            crop.save(out_crop)

            stat = ImageStat.Stat(crop)
            mean_rgb = [round(x, 1) for x in stat.mean[:3]]
            print(f"  -> Generated {out_crop} | Mean RGB: {mean_rgb}")
        else:
            print(f"  -> Failed to generate {name}")

    httpd.shutdown()
    print("All renders completed successfully!")

if __name__ == '__main__':
    run()
