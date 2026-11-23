import os
import sys
import time
import subprocess
import http.server
import socketserver
import threading
from PIL import Image, ImageStat

PORT = 5233
DIST_DIR = os.path.abspath('app/dist')
EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
OUTPUT_DIR = os.path.abspath('test_renders_v3')
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

    temp_profile = os.path.join(os.environ.get('TEMP', os.getcwd()), 'edge_render_profile_v4')
    os.makedirs(temp_profile, exist_ok=True)

    configs = [
        ('front_galaxy_overview', 'finish=galaxy&angle=front'),
        ('front_button_a_selected', 'finish=galaxy&angle=front&control=a'),
        ('front_dpad_unified_selected', 'finish=galaxy&angle=front&control=dpad'),
        ('top_trigger_l2_selected', 'finish=galaxy&angle=top&control=l2'),
    ]

    for name, query in configs:
        out_full = os.path.join(OUTPUT_DIR, f"{name}_full.png")
        out_crop = os.path.join(OUTPUT_DIR, f"{name}_stage.png")

        cmd = [
            EDGE_PATH,
            '--headless=new',
            f'--user-data-dir={temp_profile}',
            '--no-sandbox',
            '--enable-webgl',
            '--ignore-gpu-blocklist',
            '--window-size=1440,900',
            '--virtual-time-budget=6000',
            f'--screenshot={out_full}',
            f'http://127.0.0.1:{PORT}/?{query}'
        ]

        print(f"Rendering {name}...", flush=True)
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)

        if os.path.exists(out_full):
            img = Image.open(out_full)
            # Crop 3D Stage
            crop_stage = img.crop((32, 70, 720, 830))
            crop_stage.save(out_crop)

            # Specific details crops
            if name == 'front_galaxy_overview':
                # Center jewel detail crop
                jewel_crop = crop_stage.crop((300, 240, 410, 350))
                jewel_crop.save(os.path.join(OUTPUT_DIR, 'detail_nexus_jewel.png'))

                # Face buttons detail crop
                abxy_crop = crop_stage.crop((440, 310, 580, 480))
                abxy_crop.save(os.path.join(OUTPUT_DIR, 'detail_face_buttons_white.png'))

                # D-Pad dish detail crop
                dpad_crop = crop_stage.crop((190, 440, 340, 590))
                dpad_crop.save(os.path.join(OUTPUT_DIR, 'detail_dpad_dish.png'))

            stat = ImageStat.Stat(crop_stage)
            mean_rgb = [round(x, 1) for x in stat.mean[:3]]
            print(f"  -> Generated {out_crop} | Mean RGB: {mean_rgb}", flush=True)
        else:
            print(f"  -> Failed to generate {name}", flush=True)

    httpd.shutdown()
    print("All captures completed successfully!", flush=True)

if __name__ == '__main__':
    run()
