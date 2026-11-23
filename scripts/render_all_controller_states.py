import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def render_pro_controller_states():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(root, 'app', 'src', 'assets')
    out_dir = os.path.join(assets_dir, 'controller_states')
    os.makedirs(out_dir, exist_ok=True)

    front_path = os.path.join(assets_dir, 'controller_front.png')
    top_path = os.path.join(assets_dir, 'controller_top.png')

    front_img = Image.open(front_path).convert('RGBA')
    top_img = Image.open(top_path).convert('RGBA')

    fw, fh = front_img.size  # 457, 362
    tw, th = top_img.size    # 826, 385

    front_arr = np.array(front_img, dtype=np.float32)
    top_arr = np.array(top_img, dtype=np.float32)

    # Save default states
    front_img.save(os.path.join(out_dir, 'front_default.png'), 'PNG')
    top_img.save(os.path.join(out_dir, 'top_default.png'), 'PNG')
    print("Saved clean front_default.png and top_default.png")

    fy_grid, fx_grid = np.ogrid[:fh, :fw]
    ty_grid, tx_grid = np.ogrid[:th, :tw]

    # =========================================================================
    # 1. FRONT VIEW: FACE BUTTONS (A, B, X, Y)
    # Authentic 3D acrylic caps, glowing internal glyphs, crisp neon rim & light spill
    # =========================================================================
    face_buttons = {
        'front_a.png': {
            'center': (353.4, 116.3),
            'r': 19.0,
            'color': np.array([255.0, 45.0, 85.0]),  # Radiant Crimson
            'glyph_fn': lambda a, cap: cap & (a[:, :, 0] > 105) & (a[:, :, 1] < 75) & (a[:, :, 2] < 75),
        },
        'front_b.png': {
            'center': (387.1, 84.9),
            'r': 19.0,
            'color': np.array([0.0, 230.0, 118.0]),  # Emerald Green
            'glyph_fn': lambda a, cap: cap & (a[:, :, 1] > 95) & (a[:, :, 0] < 95) & (a[:, :, 2] < 85),
        },
        'front_x.png': {
            'center': (319.4, 83.1),
            'r': 19.0,
            'color': np.array([255.0, 214.0, 0.0]),  # Cyberpunk Gold
            'glyph_fn': lambda a, cap: cap & (a[:, :, 0] > 115) & (a[:, :, 1] > 115) & (a[:, :, 2] < 75),
        },
        'front_y.png': {
            'center': (353.1, 49.4),
            'r': 19.0,
            'color': np.array([0.0, 229.0, 255.0]),  # Electric Ice Cyan
            'glyph_fn': lambda a, cap: cap & (a[:, :, 2] > 125) & (a[:, :, 0] < 75),
        },
    }

    for fname, cfg in face_buttons.items():
        out = front_arr.copy()
        cx, cy = cfg['center']
        r = cfg['r']
        color = cfg['color']

        dist = np.sqrt((fx_grid - cx)**2 + (fy_grid - cy)**2)
        in_cap = dist <= r

        # Extract internal letter glyph
        glyph_mask = cfg['glyph_fn'](front_arr, in_cap)
        dark_cap = in_cap & (~glyph_mask) & (front_arr[:, :, 3] > 128)

        # Crisp neon acrylic rim ring at the button perimeter
        ring_mask = np.clip((2.2 - np.abs(dist - (r - 0.5))) / 2.2, 0.0, 1.0) ** 1.6
        # Soft, natural colored light spill on the white chassis (tinted, not blown out)
        spill_mask = np.clip((26.0 - dist) / 26.0, 0.0, 1.0) ** 2.2 * (~in_cap) * (front_arr[:, :, 3] > 128)

        for c in range(3):
            # 1. Dark plastic cap: subtle ambient reflection preserving 3D curvature and shadows
            cap_ambient = (color[c] / 255.0) * (out[:, :, c] * 0.25 + 40.0)
            out[:, :, c] = np.where(dark_cap, cap_ambient, out[:, :, c])

            # 2. Letter glyph: intense luminous backlit LED glow
            glyph_bright = np.clip(color[c] * 0.95 + 60.0, 0, 255)
            out[:, :, c] = np.where(glyph_mask, glyph_bright, out[:, :, c])

            # 3. Crisp glowing neon perimeter ring
            out[:, :, c] = np.clip(out[:, :, c] + ring_mask * color[c] * 0.95, 0, 255)

            # 4. Realistic diffuse light tint on white plastic chassis
            spill_tint = out[:, :, c] * (1.0 - spill_mask * 0.35) + color[c] * (spill_mask * 0.35)
            out[:, :, c] = np.where(spill_mask > 0.01, spill_tint, out[:, :, c])

        res_img = Image.fromarray(out.astype(np.uint8), mode='RGBA')
        res_img.save(os.path.join(out_dir, fname), 'PNG')
        print(f"Rendered {fname}")

    # =========================================================================
    # 2. FRONT VIEW: CENTER MENU BUTTON
    # Illuminated "MENU" logo + crisp violet neon ring
    # =========================================================================
    out_menu = front_arr.copy()
    mcx, mcy, mr = 227.7, 110.1, 27.0
    m_color = np.array([192.0, 132.0, 252.0]) # Cosmic Violet

    m_dist = np.sqrt((fx_grid - mcx)**2 + (fy_grid - mcy)**2)
    in_menu = (m_dist <= mr) & (front_arr[:, :, 3] > 128)
    menu_gray = np.mean(front_arr[:, :, :3], axis=2)

    is_menu_text = in_menu & (menu_gray > 42)
    is_menu_bg = in_menu & (~is_menu_text)

    m_ring = np.clip((2.5 - np.abs(m_dist - (mr - 0.5))) / 2.5, 0.0, 1.0) ** 1.6
    m_spill = np.clip((35.0 - m_dist) / 35.0, 0.0, 1.0) ** 2.2 * (~in_menu) * (front_arr[:, :, 3] > 128)

    for c in range(3):
        # Keep 3D plastic depth with subtle violet wash
        out_menu[:, :, c] = np.where(is_menu_bg, (m_color[c] / 255.0) * (out_menu[:, :, c] * 0.25 + 35.0), out_menu[:, :, c])
        # Glowing "MENU" text
        out_menu[:, :, c] = np.where(is_menu_text, np.clip(m_color[c] * 0.95 + 60.0, 0, 255), out_menu[:, :, c])
        # Outer neon rim ring
        out_menu[:, :, c] = np.clip(out_menu[:, :, c] + m_ring * m_color[c] * 0.95, 0, 255)
        # Soft chassis spill
        m_tint = out_menu[:, :, c] * (1.0 - m_spill * 0.30) + m_color[c] * (m_spill * 0.30)
        out_menu[:, :, c] = np.where(m_spill > 0.01, m_tint, out_menu[:, :, c])

    Image.fromarray(out_menu.astype(np.uint8), mode='RGBA').save(os.path.join(out_dir, 'front_menu.png'), 'PNG')
    print("Rendered front_menu.png")

    # =========================================================================
    # 3. FRONT VIEW: D-PAD WITH NATURAL 45° MITERS & CRISP NEON CONTOUR
    # Preserves 3D black cross; illuminates directional chevron and arm contour
    # =========================================================================
    dpad_cx, dpad_cy = 107.6, 101.3
    dpad_color = np.array([56.0, 189.0, 248.0]) # Sky Blue

    dist_x = np.abs(fx_grid - dpad_cx)
    dist_y = np.abs(fy_grid - dpad_cy)
    front_gray = np.mean(front_arr[:, :, :3], axis=2)
    dark_cross = (front_gray < 75) & (front_arr[:, :, 3] > 128)

    dpad_sectors = {
        'front_dpad_up.png': (fy_grid < dpad_cy) & (dist_y >= dist_x) & (dist_y <= 48) & (dist_x <= 20),
        'front_dpad_down.png': (fy_grid > dpad_cy) & (dist_y >= dist_x) & (dist_y <= 48) & (dist_x <= 20),
        'front_dpad_left.png': (fx_grid < dpad_cx) & (dist_x >= dist_y) & (dist_x <= 48) & (dist_y <= 20),
        'front_dpad_right.png': (fx_grid > dpad_cx) & (dist_x >= dist_y) & (dist_x <= 48) & (dist_y <= 20),
    }

    for fname, sector in dpad_sectors.items():
        out_dp = front_arr.copy()
        arm_mask = dark_cross & sector

        # Edge contour of the active arm
        arm_img = Image.fromarray((arm_mask * 255).astype(np.uint8), mode='L')
        arm_contour = np.array(arm_img.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.0)), dtype=np.float32) / 255.0
        # Embossed chevron arrow inside the arm
        arrow_mask = arm_mask & (front_gray > 28)

        for c in range(3):
            # 1. Subtle 25% neon wash preserving dark matte bevels
            wash = out_dp[:, :, c] * 0.75 + dpad_color[c] * 0.25
            out_dp[:, :, c] = np.where(arm_mask, wash, out_dp[:, :, c])

            # 2. Crisp glowing contour along the arm perimeter
            out_dp[:, :, c] = np.clip(out_dp[:, :, c] + arm_contour * dpad_color[c] * 1.1, 0, 255)

            # 3. Glowing embossed directional chevron arrow
            out_dp[:, :, c] = np.where(arrow_mask, np.clip(dpad_color[c] * 0.95 + 60.0, 0, 255), out_dp[:, :, c])

        Image.fromarray(out_dp.astype(np.uint8), mode='RGBA').save(os.path.join(out_dir, fname), 'PNG')
        print(f"Rendered {fname}")

    # =========================================================================
    # 4. FRONT VIEW: ANALOG STICKS (Thumb Cap Ring & Concave Dish Glow)
    # Preserves 3D knurling and mechanical socket depth
    # =========================================================================
    sticks = {
        'front_left_stick.png': (153.5, 169.2),
        'front_right_stick.png': (299.2, 172.7),
    }
    stick_color = np.array([168.0, 85.0, 247.0]) # Purple Neon

    for fname, (scx, scy) in sticks.items():
        out_st = front_arr.copy()
        s_dist = np.sqrt((fx_grid - scx)**2 + (fy_grid - scy)**2)

        # 1. Crisp glowing neon ring on the thumb cap beveled rim (r ~ 34px)
        cap_ring = np.clip((2.2 - np.abs(s_dist - 34.0)) / 2.2, 0.0, 1.0) ** 1.6

        # 2. Soft illuminated radial gradient inside the concave thumb dish (r <= 22px)
        dish_gradient = np.clip((22.0 - s_dist) / 22.0, 0.0, 1.0) ** 2.0 * 0.55

        # 3. Subtle orbital halo around the gimbal well edge (r ~ 48px)
        well_edge = np.clip((2.0 - np.abs(s_dist - 48.0)) / 2.0, 0.0, 1.0) ** 1.6 * 0.45

        stick_fx = np.clip(cap_ring * 0.95 + dish_gradient + well_edge, 0.0, 1.0)

        for c in range(3):
            out_st[:, :, c] = np.clip(out_st[:, :, c] + stick_fx * stick_color[c] * 0.90, 0, 255)

        Image.fromarray(out_st.astype(np.uint8), mode='RGBA').save(os.path.join(out_dir, fname), 'PNG')
        print(f"Rendered {fname}")

    # =========================================================================
    # 5. TOP VIEW: BUMPERS & TRIGGERS (Zero Overlap Physical Seam + Laser Contour + Glowing Text)
    # =========================================================================
    top_gray = np.mean(top_arr[:, :, :3], axis=2)
    top_dark = (top_gray < 65) & (top_arr[:, :, 3] > 128)

    # Physical diagonal seam coordinates
    r1_poly = [(65, 105), (300, 105), (295, 230), (220, 236), (160, 244), (100, 222), (65, 202)]
    r2_poly = [(65, 208), (100, 228), (160, 251), (220, 243), (300, 238), (280, 385), (85, 385)]

    # Symmetrical Right Side (L1 & L2, reflected across center tw = 826)
    l1_poly = [(tw - x, y) for (x, y) in r1_poly]
    l2_poly = [(tw - x, y) for (x, y) in r2_poly]

    def make_poly_mask(poly_pts):
        m_img = Image.new('L', (tw, th), 0)
        ImageDraw.Draw(m_img).polygon(poly_pts, fill=255)
        return np.array(m_img) > 0

    r1_plate = top_dark & make_poly_mask(r1_poly)
    r2_plate = top_dark & make_poly_mask(r2_poly)
    l1_plate = top_dark & make_poly_mask(l1_poly)
    l2_plate = top_dark & make_poly_mask(l2_poly)

    # Detect engraved text labels on bumpers & triggers
    r1_text = make_poly_mask(r1_poly) & (top_gray > 40) & (tx_grid > 140) & (tx_grid < 220) & (ty_grid > 140) & (ty_grid < 190)
    l1_text = make_poly_mask(l1_poly) & (top_gray > 40) & (tx_grid > 606) & (tx_grid < 686) & (ty_grid > 140) & (ty_grid < 190)
    r2_text = make_poly_mask(r2_poly) & (top_gray > 40) & (tx_grid > 130) & (tx_grid < 210) & (ty_grid > 260) & (ty_grid < 320)
    l2_text = make_poly_mask(l2_poly) & (top_gray > 40) & (tx_grid > 616) & (tx_grid < 696) & (ty_grid > 260) & (ty_grid < 320)

    top_controls = {
        'top_r1.png': (r1_plate, r1_text, np.array([56.0, 189.0, 248.0])),   # Sky Cyan
        'top_l1.png': (l1_plate, l1_text, np.array([56.0, 189.0, 248.0])),   # Sky Cyan
        'top_r2.png': (r2_plate, r2_text, np.array([192.0, 132.0, 252.0])),  # Purple Violet
        'top_l2.png': (l2_plate, l2_text, np.array([192.0, 132.0, 252.0])),  # Purple Violet
    }

    for fname, (plate_mask, text_mask, color) in top_controls.items():
        out_top = top_arr.copy()
        # Laser chamfer edge contour along the plate silhouette
        plate_img = Image.fromarray((plate_mask * 255).astype(np.uint8), mode='L')
        laser_edge = np.array(plate_img.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32) / 255.0

        for c in range(3):
            # 1. Subtle 30% translucent neon wash preserving matte 3D texture
            wash = out_top[:, :, c] * 0.70 + color[c] * 0.30
            out_top[:, :, c] = np.where(plate_mask, wash, out_top[:, :, c])

            # 2. Razor-sharp laser edge contour around the plate
            out_top[:, :, c] = np.clip(out_top[:, :, c] + laser_edge * color[c] * 1.25, 0, 255)

            # 3. Bright glowing engraved text ("R1", "L1", "R2", "L2")
            out_top[:, :, c] = np.where(text_mask, np.clip(color[c] * 0.95 + 60.0, 0, 255), out_top[:, :, c])

        Image.fromarray(out_top.astype(np.uint8), mode='RGBA').save(os.path.join(out_dir, fname), 'PNG')
        print(f"Rendered {fname}")

    # =========================================================================
    # 6. TOP VIEW: BLUETOOTH & HOLD BUTTONS (Glowing Logo & Contour Ring)
    # =========================================================================
    top_pills = {
        'top_bluetooth.png': {
            'center': (299.9, 162.5),
            'pw': 37, 'ph': 22,
            'color': np.array([0.0, 229.0, 255.0]), # Cyan
        },
        'top_hold.png': {
            'center': (534.1, 164.4),
            'pw': 37, 'ph': 22,
            'color': np.array([255.0, 50.0, 75.0]),  # Crimson
        },
    }

    for fname, pcfg in top_pills.items():
        out_pill = top_arr.copy()
        pcx, pcy = pcfg['center']
        pw, ph = pcfg['pw'], pcfg['ph']
        pcol = pcfg['color']

        p_dist_x = np.abs(tx_grid - pcx)
        p_dist_y = np.abs(ty_grid - pcy)
        in_pill = (p_dist_x <= pw) & (p_dist_y <= ph) & (top_arr[:, :, 3] > 128)
        p_gray = np.mean(top_arr[:, :, :3], axis=2)

        is_pill_text = in_pill & (p_gray > 70)
        is_pill_bg = in_pill & (~is_pill_text)

        pill_img = Image.fromarray((in_pill * 255).astype(np.uint8), mode='L')
        pill_contour = np.array(pill_img.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.0)), dtype=np.float32) / 255.0

        for c in range(3):
            # Subtle background wash
            out_pill[:, :, c] = np.where(is_pill_bg, out_pill[:, :, c] * 0.70 + pcol[c] * 0.30, out_pill[:, :, c])
            # Glowing white text / logo
            out_pill[:, :, c] = np.where(is_pill_text, np.clip(pcol[c] * 0.95 + 60.0, 0, 255), out_pill[:, :, c])
            # Crisp contour line
            out_pill[:, :, c] = np.clip(out_pill[:, :, c] + pill_contour * pcol[c] * 1.1, 0, 255)

        Image.fromarray(out_pill.astype(np.uint8), mode='RGBA').save(os.path.join(out_dir, fname), 'PNG')
        print(f"Rendered {fname}")

    print("\n--- Studio-grade controller states successfully generated! ---")

if __name__ == '__main__':
    render_pro_controller_states()
