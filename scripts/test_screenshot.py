import subprocess
import os
import sys

temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'edge_headless_profile')
os.makedirs(temp_dir, exist_ok=True)
out_file = os.path.abspath('test_renders/edge_test.png')
if os.path.exists(out_file):
    os.remove(out_file)

edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
html_path = os.path.abspath('test_renders/test.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html><html><body style="background:#0f172a;color:#38bdf8;"><h1>RENDER OK</h1></body></html>')

cmd = [
    edge,
    '--headless=new',
    f'--user-data-dir={temp_dir}',
    '--no-sandbox',
    '--disable-gpu',
    f'--screenshot={out_file}',
    f'file:///{html_path.replace(os.sep, "/")}'
]

print("Running command:", " ".join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
print("Return code:", res.returncode)
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)
print("File exists:", os.path.exists(out_file))
if os.path.exists(out_file):
    print("File size:", os.path.getsize(out_file))
