import os
import sys
import time
import subprocess
import http.server
import socketserver
import threading
from PIL import Image, ImageStat

PORT = 5189
DIST_DIR = os.path.abspath('app/dist')
EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
OUTPUT_DIR = os.path.abspath('test_renders')
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
    print(f"Local server started on http://127.0.0.1:{PORT}", flush=True)
    time.sleep(1)

    temp_profile = os.path.join(os.environ.get('TEMP', os.getcwd()), 'edge_render_profile_purple')
    os.makedirs(temp_profile, exist_ok=True)

    configs = [
        ('galaxy_front_overview', 'angle=front'),
        ('galaxy_button_a_hovered', 'angle=front&hover=a'),
        ('galaxy_home_selected', 'angle=front&control=home'),
    ]

    for i, (name, query) in enumerate(configs):
        out_full = os.path.join(OUTPUT_DIR, f"{name}_full.png")
        out_crop = os.path.join(OUTPUT_DIR, f"{name}_crop.png")
        if os.path.exists(out_full):
            try:
                os.remove(out_full)
            except Exception:
                pass

        sub_profile = f"{temp_profile}_{i}_{int(time.time())}"
        os.makedirs(sub_profile, exist_ok=True)

        cmd = [
            EDGE_PATH,
            '--headless=new',
            f'--user-data-dir={sub_profile}',
            '--enable-webgl',
            '--ignore-gpu-blocklist',
            '--window-size=1440,900',
            '--virtual-time-budget=5000',
            f'--screenshot={out_full}',
            f'http://127.0.0.1:{PORT}/?{query}'
        ]

        print(f"Rendering {name} ({query})...", flush=True)
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=35)

        if os.path.exists(out_full):
            img = Image.open(out_full)
            crop = img.crop((32, 70, 720, 830))
            crop.save(out_crop)

            if name == 'galaxy_front_overview':
                # Center jewel detail crop
                jewel = crop.crop((280, 220, 420, 360))
                jewel.save(os.path.join(OUTPUT_DIR, 'crop_nexus_jewel.png'))

                # ABXY buttons detail crop
                abxy = crop.crop((440, 280, 600, 470))
                abxy.save(os.path.join(OUTPUT_DIR, 'crop_abxy_white.png'))

                # D-Pad faceted dish detail crop
                dpad = crop.crop((170, 410, 340, 580))
                dpad.save(os.path.join(OUTPUT_DIR, 'crop_dpad_dish.png'))

                # Save entire app screenshot
                img.save(os.path.join(OUTPUT_DIR, 'app_full_render.png'))

            stat = ImageStat.Stat(crop)
            mean_rgb = [round(x, 1) for x in stat.mean[:3]]
            print(f"  -> Generated {out_crop} | Mean RGB: {mean_rgb}", flush=True)
        else:
            print(f"  -> Failed to generate {name}. Stderr: {res.stderr[:200]}", flush=True)

    httpd.shutdown()
    print("All renders completed successfully!", flush=True)

if __name__ == '__main__':
    run()
