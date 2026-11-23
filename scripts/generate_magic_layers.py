import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_magic_layers():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(root, 'app', 'src', 'assets')
    layers_dir = os.path.join(assets_dir, 'layers')
    os.makedirs(layers_dir, exist_ok=True)
    test_out = os.path.join(root, 'scripts', 'test_output')
    os.makedirs(test_out, exist_ok=True)

    front_path = os.path.join(assets_dir, 'controller_front.png')
    top_path = os.path.join(assets_dir, 'controller_top.png')

    front_img = Image.open(front_path).convert('RGBA')
    top_img = Image.open(top_path).convert('RGBA')

    fw, fh = front_img.size # 457, 362
    tw, th = top_img.size   # 826, 385

    front_arr = np.array(front_img, dtype=np.float32)
    front_alpha = front_arr[:, :, 3] / 255.0
    front_body = (front_alpha > 0.05).astype(np.float32)

    top_arr = np.array(top_img, dtype=np.float32)
    top_alpha = top_arr[:, :, 3] / 255.0
    top_body = (top_alpha > 0.05).astype(np.float32)

    print(f"Ingested Front: {fw}x{fh}, Top: {tw}x{th}")

    # Coordinate grid for distance math
    fy_grid, fx_grid = np.ogrid[:fh, :fw]
    ty_grid, tx_grid = np.ogrid[:th, :tw]

    # Helper to generate a button glow layer
    def make_button_glow(cx, cy, r, color_rgb, spill_r=48.0, core_boost=1.4):
        dist = np.sqrt((fx_grid - cx)**2 + (fy_grid - cy)**2)
        
        # 1. Soft radial light spill on the white matte chassis
        spill = np.clip((spill_r - dist) / spill_r, 0.0, 1.0) ** 2.0
        spill = spill * front_body * 0.55
        
        # 2. Glowing button cap interior
        core = np.clip((r - dist) / (r * 0.4), 0.0, 1.0)
        core = core * core_boost
        
        # 3. Specular acrylic ring highlight around perimeter
        ring_dist = np.abs(dist - (r - 1.5))
        ring = np.clip((3.5 - ring_dist) / 3.5, 0.0, 1.0) ** 1.5 * 0.9

        intensity = np.clip(spill + core + ring, 0.0, 1.0)
        
        layer = np.zeros((fh, fw, 4), dtype=np.uint8)
        layer[:, :, 0] = int(color_rgb[0])
        layer[:, :, 1] = int(color_rgb[1])
        layer[:, :, 2] = int(color_rgb[2])
        layer[:, :, 3] = (intensity * 255.0).astype(np.uint8)
        
        img = Image.fromarray(layer, mode='RGBA').filter(ImageFilter.GaussianBlur(1.0))
        return img

    # =========================================================================
    # FRONT VIEW LAYERS
    # =========================================================================

    # 1. Face Buttons (A: Red/Crimson, B: Emerald, X: Cyberpunk Gold, Y: Electric Cyan)
    buttons = {
        'btn_y': (353.1, 49.4, 19.0, (0, 229, 255)),     # Cyan
        'btn_b': (387.1, 84.9, 19.0, (0, 240, 120)),     # Green
        'btn_a': (353.4, 116.3, 19.0, (255, 45, 85)),    # Crimson
        'btn_x': (319.4, 83.1, 19.0, (255, 220, 0)),     # Gold
        'btn_menu': (227.7, 110.1, 27.0, (192, 132, 252)), # Violet / Purple
    }

    for name, (bx, by, br, color) in buttons.items():
        glow_img = make_button_glow(bx, by, br, color, spill_r=52.0)
        out_file = os.path.join(layers_dir, f"{name}.png")
        glow_img.save(out_file, 'PNG')
        print(f"Generated {out_file}")

    # 2. D-Pad Directional Chevrons
    # D-Pad center: 107.6, 101.3
    dpad_cx, dpad_cy = 107.6, 101.3
    dpad_arms = {
        'dpad_up': (dpad_cx, dpad_cy - 24.0, 14.0, 19.0),
        'dpad_down': (dpad_cx, dpad_cy + 24.0, 14.0, 19.0),
        'dpad_left': (dpad_cx - 24.0, dpad_cy, 19.0, 14.0),
        'dpad_right': (dpad_cx + 24.0, dpad_cy, 19.0, 14.0),
    }

    for dname, (ax, ay, aw, ah) in dpad_arms.items():
        layer = np.zeros((fh, fw, 4), dtype=np.float32)
        # Bounding box of the arm with soft falloff
        dx = np.abs(fx_grid - ax)
        dy = np.abs(fy_grid - ay)
        in_arm = (dx <= aw / 2.0) & (dy <= ah / 2.0)
        
        dist = np.sqrt(dx**2 + dy**2)
        spill = np.clip((38.0 - dist) / 38.0, 0.0, 1.0) ** 2.2 * 0.45 * front_body
        core = in_arm.astype(np.float32) * 0.85
        
        intensity = np.clip(spill + core, 0.0, 1.0)
        layer[:, :, 0] = 56.0   # Cyan Blue
        layer[:, :, 1] = 189.0
        layer[:, :, 2] = 248.0
        layer[:, :, 3] = intensity * 255.0
        
        img = Image.fromarray(layer.astype(np.uint8), mode='RGBA').filter(ImageFilter.GaussianBlur(1.2))
        out_file = os.path.join(layers_dir, f"{dname}.png")
        img.save(out_file, 'PNG')
        print(f"Generated {out_file}")

    # 3. Analog Sticks (Left Stick: 153.5, 169.2; Right Stick: 299.2, 172.7)
    sticks = {
        'stick_left': (153.5, 169.2, 34.0, (147, 51, 234)),   # Purple / Indigo
        'stick_right': (299.2, 172.7, 34.0, (147, 51, 234)),
    }

    for sname, (sx, sy, sr, scolor) in sticks.items():
        dist = np.sqrt((fx_grid - sx)**2 + (fy_grid - sy)**2)
        
        # Halo ring around gimbal well (radius between sr+4 and sr+18)
        well_dist = np.abs(dist - (sr + 10.0))
        halo = np.clip((12.0 - well_dist) / 12.0, 0.0, 1.0) ** 1.8 * 0.85
        
        # Soft center cap illumination
        cap = np.clip((sr - dist) / sr, 0.0, 1.0) * 0.45
        
        intensity = np.clip(halo + cap, 0.0, 1.0) * front_body
        layer = np.zeros((fh, fw, 4), dtype=np.uint8)
        layer[:, :, 0] = int(scolor[0])
        layer[:, :, 1] = int(scolor[1])
        layer[:, :, 2] = int(scolor[2])
        layer[:, :, 3] = (intensity * 255.0).astype(np.uint8)
        
        img = Image.fromarray(layer, mode='RGBA').filter(ImageFilter.GaussianBlur(1.5))
        out_file = os.path.join(layers_dir, f"{sname}.png")
        img.save(out_file, 'PNG')
        print(f"Generated {out_file}")

    # 4. Status Player LEDs (Front center above menu button: x ~ 228, y ~ 65)
    led_layer = np.zeros((fh, fw, 4), dtype=np.float32)
    led_xs = [207, 221, 235, 249]
    led_y = 65.0
    for lx in led_xs:
        dist = np.sqrt((fx_grid - lx)**2 + (fy_grid - led_y)**2)
        dot = np.clip((4.5 - dist) / 4.5, 0.0, 1.0) * 1.5
        halo = np.clip((14.0 - dist) / 14.0, 0.0, 1.0) ** 2.0 * 0.6
        intensity = np.clip(dot + halo, 0.0, 1.0)
        led_layer[:, :, 0] += intensity * 255.0
        led_layer[:, :, 1] += intensity * 140.0
        led_layer[:, :, 2] += intensity * 30.0
        led_layer[:, :, 3] += intensity * 255.0

    led_layer = np.clip(led_layer, 0, 255).astype(np.uint8)
    led_img = Image.fromarray(led_layer, mode='RGBA').filter(ImageFilter.GaussianBlur(0.8))
    led_out = os.path.join(layers_dir, 'led_active.png')
    led_img.save(led_out, 'PNG')
    print(f"Generated {led_out}")

    # 5. Ambient Cosmic Rim Reflection for Front
    # Detect edges of the white chassis and apply a soft purple ambient gleam
    front_edges = front_img.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(2.0))
    fe_arr = np.array(front_edges, dtype=np.float32)
    edge_strength = np.mean(fe_arr[:, :, :3], axis=2) / 255.0
    rim_layer = np.zeros((fh, fw, 4), dtype=np.uint8)
    rim_layer[:, :, 0] = 168  # Cosmic Purple
    rim_layer[:, :, 1] = 85
    rim_layer[:, :, 2] = 247
    rim_layer[:, :, 3] = (np.clip(edge_strength * 1.8, 0, 1) * front_body * 80).astype(np.uint8)
    rim_img = Image.fromarray(rim_layer, mode='RGBA')
    rim_out = os.path.join(layers_dir, 'ambient_rim_front.png')
    rim_img.save(rim_out, 'PNG')
    print(f"Generated {rim_out}")

    # =========================================================================
    # TOP VIEW LAYERS (826 x 385)
    # =========================================================================

    # 1. Bumpers (R1: x~180, y~165; L1: x~646, y~165)
    # Bumpers are wide upper wedge plates
    top_bumpers = {
        'btn_r1': (180.0, 165.0, 95.0, 55.0, (56, 189, 248)),  # Sky Cyan
        'btn_l1': (646.0, 165.0, 95.0, 55.0, (56, 189, 248)),
    }

    for bname, (bx, by, bw, bh, bcolor) in top_bumpers.items():
        layer = np.zeros((th, tw, 4), dtype=np.float32)
        dx = np.abs(tx_grid - bx)
        dy = np.abs(ty_grid - by)
        in_plate = (dx <= bw) & (dy <= bh)
        dist = np.sqrt(dx**2 + dy**2)
        
        spill = np.clip((bw * 1.4 - dist) / (bw * 1.4), 0.0, 1.0) ** 2.0 * 0.45 * top_body
        core = in_plate.astype(np.float32) * 0.75
        
        intensity = np.clip(spill + core, 0.0, 1.0)
        layer[:, :, 0] = bcolor[0]
        layer[:, :, 1] = bcolor[1]
        layer[:, :, 2] = bcolor[2]
        layer[:, :, 3] = intensity * 255.0
        
        img = Image.fromarray(layer.astype(np.uint8), mode='RGBA').filter(ImageFilter.GaussianBlur(2.0))
        out_file = os.path.join(layers_dir, f"{bname}.png")
        img.save(out_file, 'PNG')
        print(f"Generated {out_file}")

    # 2. Triggers (R2: x~160, y~290; L2: x~666, y~290)
    # Triggers are lower pull blades
    top_triggers = {
        'btn_r2': (160.0, 290.0, 85.0, 70.0, (192, 132, 252)), # Purple Neon
        'btn_l2': (666.0, 290.0, 85.0, 70.0, (192, 132, 252)),
    }

    for tname, (tx, ty, tw_p, th_p, tcolor) in top_triggers.items():
        layer = np.zeros((th, tw, 4), dtype=np.float32)
        dx = np.abs(tx_grid - tx)
        dy = np.abs(ty_grid - ty)
        in_blade = (dx <= tw_p) & (dy <= th_p)
        dist = np.sqrt(dx**2 + dy**2)
        
        spill = np.clip((tw_p * 1.5 - dist) / (tw_p * 1.5), 0.0, 1.0) ** 2.0 * 0.5 * top_body
        core = in_blade.astype(np.float32) * 0.8
        
        intensity = np.clip(spill + core, 0.0, 1.0)
        layer[:, :, 0] = tcolor[0]
        layer[:, :, 1] = tcolor[1]
        layer[:, :, 2] = tcolor[2]
        layer[:, :, 3] = intensity * 255.0
        
        img = Image.fromarray(layer.astype(np.uint8), mode='RGBA').filter(ImageFilter.GaussianBlur(2.0))
        out_file = os.path.join(layers_dir, f"{tname}.png")
        img.save(out_file, 'PNG')
        print(f"Generated {out_file}")

    # 3. Bluetooth & Hold Buttons (Top Center)
    top_pills = {
        'btn_bluetooth': (300.0, 163.0, 36.0, 22.0, (0, 229, 255)), # Cyan
        'btn_hold': (534.0, 164.0, 36.0, 22.0, (255, 60, 60)),     # Red
    }

    for pname, (px, py, pw, ph, pcolor) in top_pills.items():
        layer = np.zeros((th, tw, 4), dtype=np.float32)
        dx = np.abs(tx_grid - px)
        dy = np.abs(ty_grid - py)
        dist = np.sqrt(dx**2 + dy**2)
        
        core = ((dx <= pw) & (dy <= ph)).astype(np.float32) * 0.9
        spill = np.clip((45.0 - dist) / 45.0, 0.0, 1.0) ** 2.0 * 0.45 * top_body
        
        intensity = np.clip(spill + core, 0.0, 1.0)
        layer[:, :, 0] = pcolor[0]
        layer[:, :, 1] = pcolor[1]
        layer[:, :, 2] = pcolor[2]
        layer[:, :, 3] = intensity * 255.0
        
        img = Image.fromarray(layer.astype(np.uint8), mode='RGBA').filter(ImageFilter.GaussianBlur(1.2))
        out_file = os.path.join(layers_dir, f"{pname}.png")
        img.save(out_file, 'PNG')
        print(f"Generated {out_file}")

    # =========================================================================
    # CREATE COMPOSITE PREVIEW (ALL BUTTONS ON) FOR VISUAL VERIFICATION
    # =========================================================================
    preview_front = front_img.copy()
    for fname in ['btn_a', 'btn_b', 'btn_x', 'btn_y', 'dpad_up', 'dpad_down', 'dpad_left', 'dpad_right', 'stick_left', 'stick_right', 'btn_menu', 'led_active', 'ambient_rim_front']:
        layer = Image.open(os.path.join(layers_dir, f"{fname}.png"))
        preview_front.alpha_composite(layer)
    preview_front.save(os.path.join(test_out, 'preview_all_front.png'))
    print(f"Generated composite preview: {os.path.join(test_out, 'preview_all_front.png')}")

    preview_top = top_img.copy()
    for tname in ['btn_r1', 'btn_l1', 'btn_r2', 'btn_l2', 'btn_bluetooth', 'btn_hold']:
        layer = Image.open(os.path.join(layers_dir, f"{tname}.png"))
        preview_top.alpha_composite(layer)
    preview_top.save(os.path.join(test_out, 'preview_all_top.png'))
    print(f"Generated composite preview: {os.path.join(test_out, 'preview_all_top.png')}")

if __name__ == '__main__':
    create_magic_layers()
