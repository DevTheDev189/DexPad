import os
import json
from collections import deque
import numpy as np
from PIL import Image, ImageDraw

def process_and_detect():
    img1_path = r'C:/Users/dwinslow/.gemini/antigravity/brain/6536fc45-1be5-4938-a6ac-e824553da8c8/.user_uploaded/media_1794804098807_4e2f5db0.png'
    img2_path = r'C:/Users/dwinslow/.gemini/antigravity/brain/6536fc45-1be5-4938-a6ac-e824553da8c8/.user_uploaded/media_1794804112525_430ecf4e.png'

    app_assets = r'C:/Users/dwinslow/Documents/Dexter_Controller_Project/app/src/assets'
    os.makedirs(app_assets, exist_ok=True)

    # -------------------------------------------------------------------------
    # 1. FRONT VIEW
    # -------------------------------------------------------------------------
    front_img = Image.open(img1_path).convert('RGBA')
    front_arr = np.array(front_img)
    alpha = front_arr[:, :, 3]

    ys, xs = np.where(alpha > 0)
    x0, x1 = int(xs.min()), int(xs.max() + 1)
    y0, y1 = int(ys.min()), int(ys.max() + 1)

    front_cropped_arr = front_arr[y0:y1, x0:x1]
    front_crop_h, front_crop_w = front_cropped_arr.shape[:2]
    front_cropped_img = Image.fromarray(front_cropped_arr, mode='RGBA')
    front_save_path = os.path.join(app_assets, 'controller_front.png')
    front_cropped_img.save(front_save_path, 'PNG')
    print(f"[FRONT] Cropped to size: {front_crop_w}x{front_crop_h} (saved to {front_save_path})")

    rgb = front_cropped_arr[:, :, :3].astype(np.float32)
    gray = np.mean(rgb, axis=2)
    crop_alpha = front_cropped_arr[:, :, 3]

    dark = (gray < 85) & (crop_alpha > 128)
    labeled = np.zeros((front_crop_h, front_crop_w), dtype=int)
    cur_label = 0
    front_comps = []

    for y in range(front_crop_h):
        for x in range(front_crop_w):
            if dark[y, x] and labeled[y, x] == 0:
                cur_label += 1
                q = deque([(y, x)])
                labeled[y, x] = cur_label
                pix = []
                while q:
                    cy, cx = q.popleft()
                    pix.append((cy, cx))
                    for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                        if 0 <= ny < front_crop_h and 0 <= nx < front_crop_w:
                            if dark[ny, nx] and labeled[ny, nx] == 0:
                                labeled[ny, nx] = cur_label
                                q.append((ny, nx))
                if len(pix) > 25:
                    p_arr = np.array(pix)
                    cy, cx = p_arr.mean(axis=0)
                    front_comps.append({
                        'count': len(pix),
                        'centroid': (float(cx), float(cy)),
                        'bbox': (int(p_arr[:, 1].min()), int(p_arr[:, 0].min()), int(p_arr[:, 1].max()), int(p_arr[:, 0].max())),
                        'w': int(p_arr[:, 1].max() - p_arr[:, 1].min() + 1),
                        'h': int(p_arr[:, 0].max() - p_arr[:, 0].min() + 1),
                        'pixels': p_arr
                    })

    # D-Pad
    dpad = [c for c in front_comps if c['count'] > 4000][0]
    dpad_cx, dpad_cy = dpad['centroid']
    dpad_w = dpad['w']

    # Thumbsticks
    sticks = [c for c in front_comps if 2500 < c['count'] < 4000]
    sticks.sort(key=lambda c: c['centroid'][0])
    l_stick = sticks[0]
    r_stick = sticks[1]

    # Menu button
    menu_btn = [c for c in front_comps if 1800 < c['count'] < 2600][0]

    # Face buttons
    face_btns = [c for c in front_comps if 600 < c['count'] < 1300 and c['centroid'][0] > 260]
    face_btns.sort(key=lambda c: c['centroid'][1])
    btn_y = min(face_btns, key=lambda c: c['centroid'][1])
    btn_a = max(face_btns, key=lambda c: c['centroid'][1])
    btn_x = min(face_btns, key=lambda c: c['centroid'][0])
    btn_b = max(face_btns, key=lambda c: c['centroid'][0])

    # Shoulder Bumpers L1 / R1
    bumpers = [c for c in front_comps if 300 < c['count'] < 700 and c['centroid'][1] < 30]
    bumpers.sort(key=lambda c: c['centroid'][0])
    l1 = bumpers[0] if len(bumpers) >= 1 else None
    r1 = bumpers[1] if len(bumpers) >= 2 else None

    dpad_arm_offset = dpad_w * 0.31

    front_points = {
        'y': (btn_y['centroid'][0], btn_y['centroid'][1], btn_y['w']),
        'a': (btn_a['centroid'][0], btn_a['centroid'][1], btn_a['w']),
        'x': (btn_x['centroid'][0], btn_x['centroid'][1], btn_x['w']),
        'b': (btn_b['centroid'][0], btn_b['centroid'][1], btn_b['w']),
        'left_stick': (l_stick['centroid'][0], l_stick['centroid'][1], l_stick['w']),
        'right_stick': (r_stick['centroid'][0], r_stick['centroid'][1], r_stick['w']),
        'menu': (menu_btn['centroid'][0], menu_btn['centroid'][1], menu_btn['w']),
        'home': (menu_btn['centroid'][0], menu_btn['centroid'][1], menu_btn['w']),
        'options': (menu_btn['centroid'][0] - 50, menu_btn['centroid'][1] + 28, 22),
        'dpad_up': (dpad_cx, dpad_cy - dpad_arm_offset, 28),
        'dpad_down': (dpad_cx, dpad_cy + dpad_arm_offset, 28),
        'dpad_left': (dpad_cx - dpad_arm_offset, dpad_cy, 28),
        'dpad_right': (dpad_cx + dpad_arm_offset, dpad_cy, 28),
        'l1': (l1['centroid'][0], l1['centroid'][1] + 6, 34) if l1 else (104.0, 10.0, 34),
        'r1': (r1['centroid'][0], r1['centroid'][1] + 6, 34) if r1 else (353.0, 10.0, 34),
        'l2': (l1['centroid'][0] - 32, l1['centroid'][1] - 4, 34) if l1 else (72.0, 6.0, 34),
        'r2': (r1['centroid'][0] + 32, r1['centroid'][1] - 4, 34) if r1 else (385.0, 6.0, 34),
    }

    front_hotspots = {}
    for k, (px, py, diam) in front_points.items():
        front_hotspots[k] = {
            'x': round((px / front_crop_w) * 100, 2),
            'y': round((py / front_crop_h) * 100, 2),
            'sizePercent': round((diam / front_crop_w) * 100, 2),
            'px_x': round(px, 1),
            'px_y': round(py, 1),
            'size_px': int(diam)
        }

    annotated_front = front_cropped_img.copy()
    draw_f = ImageDraw.Draw(annotated_front)
    for k, info in front_hotspots.items():
        cx = info['px_x']
        cy = info['px_y']
        r = info['size_px'] / 2.0
        draw_f.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 255, 120, 255), width=2)
        draw_f.text((cx - 8, cy - 5), k, fill=(0, 255, 120, 255))
    annotated_front.save(os.path.join(app_assets, 'verify_front.png'), 'PNG')
    print(f"[FRONT] Verification overlay saved to {os.path.join(app_assets, 'verify_front.png')}")

    # -------------------------------------------------------------------------
    # 2. TOP VIEW
    # -------------------------------------------------------------------------
    top_img = Image.open(img2_path).convert('RGBA')
    top_arr = np.array(top_img)
    top_alpha = top_arr[:, :, 3]

    ys_t, xs_t = np.where(top_alpha > 0)
    tx0, tx1 = int(xs_t.min()), int(xs_t.max() + 1)
    ty0, ty1 = int(ys_t.min()), int(ys_t.max() + 1)

    top_cropped_arr = top_arr[ty0:ty1, tx0:tx1]
    top_crop_h, top_crop_w = top_cropped_arr.shape[:2]
    top_cropped_img = Image.fromarray(top_cropped_arr, mode='RGBA')
    top_save_path = os.path.join(app_assets, 'controller_top.png')
    top_cropped_img.save(top_save_path, 'PNG')
    print(f"\n[TOP] Cropped to size: {top_crop_w}x{top_crop_h} (saved to {top_save_path})")

    # On Top View:
    # Right-hand side of the image has L1 (upper wedge) and L2 (lower wedge)
    # Left-hand side of the image has R1 (upper wedge) and R2 (lower wedge)
    # Center has Bluetooth button (x ~ 295, y ~ 164) and HOLD button (x ~ 530, y ~ 164)
    top_points = {
        'r1': (180.0, 185.0, 65),
        'r2': (168.0, 285.0, 70),
        'l1': (646.0, 185.0, 65),
        'l2': (658.0, 285.0, 70),
        'home': (295.0, 164.0, 50),
        'options': (530.0, 164.0, 50),
    }

    top_hotspots = {}
    for k, (px, py, diam) in top_points.items():
        top_hotspots[k] = {
            'x': round((px / top_crop_w) * 100, 2),
            'y': round((py / top_crop_h) * 100, 2),
            'sizePercent': round((diam / top_crop_w) * 100, 2),
            'px_x': round(px, 1),
            'px_y': round(py, 1),
            'size_px': int(diam)
        }

    annotated_top = top_cropped_img.copy()
    draw_t = ImageDraw.Draw(annotated_top)
    for k, info in top_hotspots.items():
        cx = info['px_x']
        cy = info['px_y']
        r = info['size_px'] / 2.0
        draw_t.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 255, 120, 255), width=2)
        draw_t.text((cx - 8, cy - 5), k, fill=(0, 255, 120, 255))
    annotated_top.save(os.path.join(app_assets, 'verify_top.png'), 'PNG')
    print(f"[TOP] Verification overlay saved to {os.path.join(app_assets, 'verify_top.png')}")

    return {
        'front': {
            'crop_size': (front_crop_w, front_crop_h),
            'hotspots': front_hotspots
        },
        'top': {
            'crop_size': (top_crop_w, top_crop_h),
            'hotspots': top_hotspots
        }
    }

if __name__ == '__main__':
    res = process_and_detect()
    print("\n--- FRONT HOTSPOTS ---")
    for k, v in res['front']['hotspots'].items():
        print(f"  {{ id: '{k}', label: '{k.upper()}', x: {v['x']}, y: {v['y']}, sizePercent: {v['sizePercent']} }},")

    print("\n--- TOP HOTSPOTS ---")
    for k, v in res['top']['hotspots'].items():
        print(f"  {{ id: '{k}', label: '{k.upper()}', x: {v['x']}, y: {v['y']}, sizePercent: {v['sizePercent']} }},")
