import os
import json
from collections import deque
import numpy as np
from PIL import Image, ImageDraw

def clean_extract_and_detect(input_path, output_png_path, view_type='front'):
    """
    1. Removes background completely via BFS floodfill and alpha anti-aliasing.
    2. Crops tightly to the controller bounding box.
    3. Runs edge / dark region detection to find exact button centroids and sizes.
    """
    img = Image.open(input_path).convert('RGB')
    w, h = img.size
    rgb = np.array(img, dtype=np.float32)

    # 1. Background color detection from all 4 borders
    borders = np.vstack([rgb[0, :], rgb[-1, :], rgb[:, 0], rgb[:, -1]])
    bg_color = np.median(borders, axis=0)
    print(f"[{view_type.upper()}] Image size: {w}x{h}, BG median RGB: {bg_color}")

    dist = np.linalg.norm(rgb - bg_color, axis=2)

    # 2. BFS flood fill from image perimeter
    is_pure_bg = dist < 5.5
    visited = np.zeros((h, w), dtype=bool)
    q = deque()

    for x in range(w):
        if is_pure_bg[0, x]:
            visited[0, x] = True
            q.append((0, x))
        if is_pure_bg[h - 1, x]:
            visited[h - 1, x] = True
            q.append((h - 1, x))

    for y in range(h):
        if is_pure_bg[y, 0] and not visited[y, 0]:
            visited[y, 0] = True
            q.append((y, 0))
        if is_pure_bg[y, w - 1] and not visited[y, w - 1]:
            visited[y, w - 1] = True
            q.append((y, w - 1))

    while q:
        cy, cx = q.popleft()
        for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
            if 0 <= ny < h and 0 <= nx < w:
                if not visited[ny, nx] and is_pure_bg[ny, nx]:
                    visited[ny, nx] = True
                    q.append((ny, nx))

    bg_pixel_count = np.sum(visited)
    print(f"[{view_type.upper()}] Outer background removed: {bg_pixel_count} px ({bg_pixel_count / (w * h) * 100:.2f}%)")

    # 3. Alpha calculation with edge anti-aliasing & halo decontamination
    alpha = np.ones((h, w), dtype=np.float32) * 255.0
    alpha[visited] = 0.0

    # Soften transition on 1-pixel boundary
    clean_rgb = np.copy(rgb)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if not visited[y, x]:
                # If adjacent to outer background
                if visited[y-1, x] or visited[y+1, x] or visited[y, x-1] or visited[y, x+1]:
                    d = dist[y, x]
                    if d < 22.0:
                        a_norm = np.clip((d - 1.5) / (22.0 - 1.5), 0.0, 1.0)
                        alpha[y, x] = a_norm * 255.0
                        # Un-premultiply background color to eliminate white fringe
                        denom = max(a_norm, 0.08)
                        for c in range(3):
                            clean_rgb[y, x, c] = np.clip((rgb[y, x, c] - (1.0 - a_norm) * bg_color[c]) / denom, 0.0, 255.0)

    # 4. Tight Crop to Controller Bounds
    solid_mask = alpha > 0
    ys, xs = np.where(solid_mask)
    x0, x1 = int(xs.min()), int(xs.max() + 1)
    y0, y1 = int(ys.min()), int(ys.max() + 1)

    crop_w = x1 - x0
    crop_h = y1 - y0
    print(f"[{view_type.upper()}] Tight Crop: ({x0}, {y0}) to ({x1}, {y1}), Size = {crop_w}x{crop_h}")

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = np.clip(clean_rgb, 0, 255).astype(np.uint8)
    rgba[:, :, 3] = np.clip(alpha, 0, 255).astype(np.uint8)

    cropped_rgba = rgba[y0:y1, x0:x1]
    cropped_img = Image.fromarray(cropped_rgba, mode='RGBA')
    os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
    cropped_img.save(output_png_path, 'PNG')
    print(f"[{view_type.upper()}] Successfully saved transparent PNG to {output_png_path}")

    # 5. Edge / Dark Feature Detection on Controller
    # Convert cropped area to grayscale
    cropped_rgb = clean_rgb[y0:y1, x0:x1]
    gray = np.mean(cropped_rgb, axis=2)
    cropped_mask = (alpha[y0:y1, x0:x1] > 128)

    # Black buttons on white shell: threshold gray < 85
    dark = (gray < 85) & cropped_mask

    # Connected component labeling
    labeled = np.zeros((crop_h, crop_w), dtype=int)
    cur_label = 0
    components = []

    for y in range(crop_h):
        for x in range(crop_w):
            if dark[y, x] and labeled[y, x] == 0:
                cur_label += 1
                q = deque([(y, x)])
                labeled[y, x] = cur_label
                pix = []
                while q:
                    cy, cx = q.popleft()
                    pix.append((cy, cx))
                    for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                        if 0 <= ny < crop_h and 0 <= nx < crop_w:
                            if dark[ny, nx] and labeled[ny, nx] == 0:
                                labeled[ny, nx] = cur_label
                                q.append((ny, nx))
                if len(pix) > 35:
                    p_arr = np.array(pix)
                    cy, cx = p_arr.mean(axis=0)
                    components.append({
                        'count': len(pix),
                        'centroid': (float(cx), float(cy)),
                        'bbox': (int(p_arr[:, 1].min()), int(p_arr[:, 0].min()), int(p_arr[:, 1].max()), int(p_arr[:, 0].max())),
                        'width': int(p_arr[:, 1].max() - p_arr[:, 1].min() + 1),
                        'height': int(p_arr[:, 0].max() - p_arr[:, 0].min() + 1)
                    })

    hotspots = {}

    if view_type == 'front':
        # Left and Right Thumbsticks (clusters of ~7000 px, cx separated)
        sticks = [c for c in components if 5000 < c['count'] < 9000]
        sticks.sort(key=lambda c: c['centroid'][0])
        l_stick = sticks[0]
        r_stick = sticks[1]

        # D-pad (cluster of ~10000 px on left half)
        dpad = [c for c in components if c['count'] > 9500][0]
        dpad_cx, dpad_cy = dpad['centroid']
        dpad_w = dpad['width']

        # Face buttons (4 circular clusters on right half: count 1400-2600, cx > 400 in crop)
        face_btns = [c for c in components if 1400 < c['count'] < 2600 and c['centroid'][0] > 400]
        btn_y = min(face_btns, key=lambda c: c['centroid'][1])
        btn_a = max(face_btns, key=lambda c: c['centroid'][1])
        btn_x = min(face_btns, key=lambda c: c['centroid'][0])
        btn_b = max(face_btns, key=lambda c: c['centroid'][0])

        # Center Emblem / Home button
        home = [c for c in components if 4000 < c['count'] < 5500][0]

        # Bumpers L1 and R1 (top edges in crop, y < 40)
        bumpers = [c for c in components if 700 < c['count'] < 1300 and c['centroid'][1] < 40]
        bumpers.sort(key=lambda c: c['centroid'][0])
        l1 = bumpers[0]
        r1 = bumpers[1]

        # Menu and Options buttons: small buttons around y ~ 216
        nav_btns = [c for c in components if 35 <= c['count'] < 120 and 190 < c['centroid'][1] < 240]
        nav_btns.sort(key=lambda c: c['centroid'][0])
        options = nav_btns[0] if len(nav_btns) >= 1 else None
        menu = nav_btns[-1] if len(nav_btns) >= 2 else None

        # Build detected coordinate map (exact pixels in cropped image)
        pts = {
            'y': (btn_y['centroid'][0], btn_y['centroid'][1], btn_y['width']),
            'a': (btn_a['centroid'][0], btn_a['centroid'][1], btn_a['width']),
            'x': (btn_x['centroid'][0], btn_x['centroid'][1], btn_x['width']),
            'b': (btn_b['centroid'][0], btn_b['centroid'][1], btn_b['width']),
            'left_stick': (l_stick['centroid'][0], l_stick['centroid'][1], l_stick['width']),
            'right_stick': (r_stick['centroid'][0], r_stick['centroid'][1], r_stick['width']),
            'dpad_up': (dpad_cx, dpad_cy - dpad_w * 0.31, 36),
            'dpad_down': (dpad_cx, dpad_cy + dpad_w * 0.31, 36),
            'dpad_left': (dpad_cx - dpad_w * 0.31, dpad_cy, 36),
            'dpad_right': (dpad_cx + dpad_w * 0.31, dpad_cy, 36),
            'home': (home['centroid'][0], home['centroid'][1], home['width']),
            'options': (options['centroid'][0], options['centroid'][1], 24) if options else (255.0, 216.0, 24),
            'menu': (menu['centroid'][0], menu['centroid'][1], 24) if menu else (407.0, 216.0, 24),
            'l1': (l1['centroid'][0], l1['centroid'][1] + 10, 42),
            'r1': (r1['centroid'][0], r1['centroid'][1] + 10, 42),
            'l2': (l1['centroid'][0] - 45, l1['centroid'][1] - 8, 44),
            'r2': (r1['centroid'][0] + 45, r1['centroid'][1] - 8, 44),
        }

        # Convert to percentages
        for k, (px, py, diam) in pts.items():
            hotspots[k] = {
                'x': round((px / crop_w) * 100, 2),
                'y': round((py / crop_h) * 100, 2),
                'size': int(diam),
                'px_x': round(px, 1),
                'px_y': round(py, 1),
            }

    elif view_type == 'top':
        # In top view:
        # L2 and R2 are large trigger tabs at y ~ 45 in crop
        # L1 and R1 are bumpers at y ~ 238 in crop
        # Home/pairing button at center (x ~ 598, y ~ 233)
        triggers = [c for c in components if 8000 < c['count'] < 12000 and c['centroid'][1] < 100]
        triggers.sort(key=lambda c: c['centroid'][0])
        l2 = triggers[0] if len(triggers) >= 1 else None
        r2 = triggers[1] if len(triggers) >= 2 else None

        bumpers = [c for c in components if 4000 < c['count'] < 7000 and 180 < c['centroid'][1] < 280]
        bumpers.sort(key=lambda c: c['centroid'][0])
        l1 = bumpers[0] if len(bumpers) >= 1 else None
        r1 = bumpers[1] if len(bumpers) >= 2 else None

        pts = {
            'l2': (l2['centroid'][0], l2['centroid'][1], 60) if l2 else (415.0, 45.0, 60),
            'r2': (r2['centroid'][0], r2['centroid'][1], 60) if r2 else (780.0, 45.0, 60),
            'l1': (l1['centroid'][0], l1['centroid'][1], 55) if l1 else (427.0, 238.0, 55),
            'r1': (r1['centroid'][0], r1['centroid'][1], 55) if r1 else (769.0, 238.0, 55),
            'home': (598.0, 233.0, 45),
        }

        for k, (px, py, diam) in pts.items():
            hotspots[k] = {
                'x': round((px / crop_w) * 100, 2),
                'y': round((py / crop_h) * 100, 2),
                'size': int(diam),
                'px_x': round(px, 1),
                'px_y': round(py, 1),
            }

    # Generate visual verification image with green alignment circles
    annotated = cropped_img.copy()
    draw = ImageDraw.Draw(annotated)
    for k, info in hotspots.items():
        cx = info['px_x']
        cy = info['px_y']
        r = info['size'] / 2.0
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 255, 120, 255), width=2)
        draw.text((cx - 10, cy - 6), k, fill=(0, 255, 120, 255))

    verify_path = os.path.join(os.path.dirname(output_png_path), f"verify_{view_type}.png")
    annotated.save(verify_path, 'PNG')
    print(f"[{view_type.upper()}] Verification overlay saved to {verify_path}")

    return {
        'crop_size': (crop_w, crop_h),
        'hotspots': hotspots
    }

if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    front_raw = os.path.join(root_dir, 'steelseries-nimbus-wireless-gaming-controller-apple-white-3d-model-61b29ae687.webp')
    top_raw = os.path.join(root_dir, 'steelseries-nimbus-wireless-gaming-controller-apple-white-3d-model-9908df8abd.webp')

    front_out = os.path.join(root_dir, 'app', 'src', 'assets', 'controller_front.png')
    top_out = os.path.join(root_dir, 'app', 'src', 'assets', 'controller_top.png')

    front_res = clean_extract_and_detect(front_raw, front_out, 'front')
    top_res = clean_extract_and_detect(top_raw, top_out, 'top')

    results = {
        'front': front_res,
        'top': top_res
    }

    results_json = os.path.join(root_dir, 'scripts', 'detected_hotspots.json')
    with open(results_json, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n--- FRONT HOTSPOTS ---")
    for k, v in front_res['hotspots'].items():
        print(f"  {k}: {{ x: {v['x']}, y: {v['y']}, size: {v['size']} }}")

    print("\n--- TOP HOTSPOTS ---")
    for k, v in top_res['hotspots'].items():
        print(f"  {k}: {{ x: {v['x']}, y: {v['y']}, size: {v['size']} }}")
