import os
import math
import FreeCAD
import Part
import Mesh
import Draft

def build_complete_case():
    doc = FreeCAD.newDocument("pico2w_enclosure_goth")

    # -------------------------------------------------------------
    # 1. PARAMETRIC COFFIN SILHOUETTE WITH INTEGRATED BAT WINGS
    # -------------------------------------------------------------
    # Total length: 56.0 mm (Y from 0 to 56.0)
    # Cavity: 21.7 mm wide (X from -10.85 to +10.85), 51.7 mm long (Y from 1.8 to 53.5)
    def make_coffin_polygon():
        pts_right = [
            FreeCAD.Vector(0, 0, 0),
            FreeCAD.Vector(12.7, 0, 0),         # Foot corner (W = 25.4 mm)
            FreeCAD.Vector(14.5, 36.0, 0),      # Lower flank (W = 29.0 mm)
            FreeCAD.Vector(16.5, 41.5, 0),      # Primary wingtip flare (W = 33.0 mm)
            FreeCAD.Vector(15.0, 44.0, 0),      # Wing scallop notch (W = 30.0 mm)
            FreeCAD.Vector(15.6, 46.5, 0),      # Secondary wingtip (W = 31.2 mm)
            FreeCAD.Vector(14.0, 49.0, 0),      # Upper shoulder (W = 28.0 mm)
            FreeCAD.Vector(12.7, 56.0, 0),      # Head corner (W = 25.4 mm)
            FreeCAD.Vector(0, 56.0, 0),         # Head center
        ]
        pts_left = [FreeCAD.Vector(-p.x, p.y, 0) for p in reversed(pts_right[1:-1])]
        all_pts = pts_right + pts_left + [pts_right[0]]
        wire = Part.Wire(Part.makePolygon(all_pts))
        face = Part.Face(wire)
        return face

    # -------------------------------------------------------------
    # 2. AUTHENTIC MICRO-USB CUTTER
    # -------------------------------------------------------------
    def make_microusb_cutter(z_center):
        def microusb_wire(w_top, h, chamfer, y):
            w_bot = w_top - 2.0 * chamfer
            h_half = h / 2.0
            pts = [
                FreeCAD.Vector(-w_top/2.0, y, h_half),
                FreeCAD.Vector(w_top/2.0, y, h_half),
                FreeCAD.Vector(w_top/2.0, y, -h_half + chamfer),
                FreeCAD.Vector(w_bot/2.0, y, -h_half),
                FreeCAD.Vector(-w_bot/2.0, y, -h_half),
                FreeCAD.Vector(-w_top/2.0, y, -h_half + chamfer),
                FreeCAD.Vector(-w_top/2.0, y, h_half)
            ]
            return Part.Wire(Part.makePolygon(pts))
        
        w_outer = microusb_wire(10.8, 5.0, 1.3, 56.5)
        w_bevel = microusb_wire(8.0, 3.2, 0.85, 54.8)
        w_inner = microusb_wire(8.0, 3.2, 0.85, 52.0)
        cutter = Part.makeLoft([w_inner, w_bevel, w_outer], True)
        cutter.translate(FreeCAD.Vector(0, 0, z_center))
        return cutter

    # -------------------------------------------------------------
    # 3. CAMERA-STYLE CONCAVE WELL CUTTER
    # -------------------------------------------------------------
    def make_revolved_well(r_hole, r_dish, depth, lip_r, z_top):
        n_pts = 16
        pts = [
            FreeCAD.Vector(0, 0, -1.0),
            FreeCAD.Vector(r_hole, 0, -1.0),
            FreeCAD.Vector(r_hole, 0, z_top - depth)
        ]
        for i in range(1, n_pts + 1):
            t = i / float(n_pts)
            r = r_hole + (r_dish + lip_r - r_hole) * t
            s = (1.0 - math.cos(t * math.pi)) / 2.0
            z = (z_top - depth) + (depth + 0.1) * s
            pts.append(FreeCAD.Vector(r, 0, z))
        pts.append(FreeCAD.Vector(0, 0, z_top + 0.1))
        pts.append(FreeCAD.Vector(0, 0, -1.0))
        wire = Part.Wire(Part.makePolygon(pts))
        face = Part.Face(wire)
        return face.revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 360)

    # -------------------------------------------------------------
    # 4. ORGANIC DRIPPING SLIME ("MELT/DRIP" EFFECT)
    # -------------------------------------------------------------
    def make_drip_solid(z_base, h_drip):
        # Multi-point smooth organic dripping drape
        # 5 distinct rounded droplets cascading downwards
        pts = [
            FreeCAD.Vector(-12.5, 56.0, 0),
            FreeCAD.Vector(12.5, 56.0, 0),
            FreeCAD.Vector(13.8, 49.0, 0),
            FreeCAD.Vector(14.8, 44.0, 0),
            # Droplet 1 (right shoulder):
            FreeCAD.Vector(14.2, 40.0, 0),
            FreeCAD.Vector(13.2, 38.5, 0),
            FreeCAD.Vector(12.2, 40.0, 0),
            # Valley 1:
            FreeCAD.Vector(10.8, 44.0, 0),
            # Droplet 2 (right center):
            FreeCAD.Vector(8.8, 41.5, 0),
            FreeCAD.Vector(7.5, 39.5, 0),
            FreeCAD.Vector(6.2, 41.5, 0),
            # Valley 2:
            FreeCAD.Vector(4.2, 44.5, 0),
            # Droplet 3 (center long drip):
            FreeCAD.Vector(1.5, 39.0, 0),
            FreeCAD.Vector(0.0, 36.5, 0),
            FreeCAD.Vector(-1.5, 39.0, 0),
            # Valley 3:
            FreeCAD.Vector(-3.8, 44.0, 0),
            # Droplet 4 (left center):
            FreeCAD.Vector(-5.8, 41.0, 0),
            FreeCAD.Vector(-7.2, 39.0, 0),
            FreeCAD.Vector(-8.6, 41.0, 0),
            # Valley 4:
            FreeCAD.Vector(-10.2, 44.0, 0),
            # Droplet 5 (left shoulder):
            FreeCAD.Vector(-12.0, 40.5, 0),
            FreeCAD.Vector(-13.2, 39.0, 0),
            FreeCAD.Vector(-14.2, 41.0, 0),
            FreeCAD.Vector(-14.8, 44.0, 0),
            FreeCAD.Vector(-13.8, 49.0, 0),
            FreeCAD.Vector(-12.5, 56.0, 0)
        ]
        wire = Part.Wire(Part.makePolygon(pts))
        face = Part.Face(wire)
        solid = face.extrude(FreeCAD.Vector(0, 0, h_drip))
        solid.translate(FreeCAD.Vector(0, 0, z_base))
        return solid

    # -------------------------------------------------------------
    # 5. GOTHIC MOTIFS (BAT CREST, X-PATCH, STITCHES, BROKEN HEART)
    # -------------------------------------------------------------
    def make_bat_crest(cx, cy, w, h, depth, z_base):
        w2 = w / 2.0
        h2 = h / 2.0
        pts_r = [
            FreeCAD.Vector(0.0, h2 * 0.45, 0),
            FreeCAD.Vector(w2 * 0.14, h2 * 0.95, 0),  # ear tip
            FreeCAD.Vector(w2 * 0.24, h2 * 0.40, 0),  # ear notch
            FreeCAD.Vector(w2 * 0.60, h2 * 0.85, 0),  # upper wing curve
            FreeCAD.Vector(w2 * 1.0, h2 * 1.0, 0),    # wingtip
            FreeCAD.Vector(w2 * 0.84, h2 * 0.25, 0),  # scallop tip 1
            FreeCAD.Vector(w2 * 0.70, h2 * 0.42, 0),  # cusp 1
            FreeCAD.Vector(w2 * 0.54, -h2 * 0.20, 0), # scallop tip 2
            FreeCAD.Vector(w2 * 0.38, 0.0, 0),        # cusp 2
            FreeCAD.Vector(w2 * 0.22, -h2 * 0.65, 0), # scallop tip 3
            FreeCAD.Vector(w2 * 0.12, -h2 * 0.30, 0), # lower join
            FreeCAD.Vector(0.0, -h2 * 0.85, 0)        # tail
        ]
        pts_l = [FreeCAD.Vector(-p.x, p.y, 0) for p in reversed(pts_r[1:-1])]
        all_pts = pts_r + pts_l + [pts_r[0]]
        w_bat = Part.Wire(Part.makePolygon(all_pts))
        f_bat = Part.Face(w_bat)
        s_bat = f_bat.extrude(FreeCAD.Vector(0, 0, depth))
        s_bat.translate(FreeCAD.Vector(cx, cy, z_base))
        return s_bat

    def make_x_patch(cx, cy, size, bar_w, h, z_base):
        # Beveled crossing bars with rounded ends
        b1 = Part.makeBox(size, bar_w, h)
        b1.translate(FreeCAD.Vector(-size/2.0, -bar_w/2.0, 0))
        # Round the ends of the bar
        ve1 = [e for e in b1.Edges if abs(e.Length - h) < 0.01 and (abs(e.Vertexes[0].Point.x - size/2.0) < 0.01 or abs(e.Vertexes[0].Point.x + size/2.0) < 0.01)]
        if len(ve1) == 4:
            b1 = b1.makeFillet(bar_w * 0.45, ve1)
        b1.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 45)
        
        b2 = Part.makeBox(size, bar_w, h)
        b2.translate(FreeCAD.Vector(-size/2.0, -bar_w/2.0, 0))
        ve2 = [e for e in b2.Edges if abs(e.Length - h) < 0.01 and (abs(e.Vertexes[0].Point.x - size/2.0) < 0.01 or abs(e.Vertexes[0].Point.x + size/2.0) < 0.01)]
        if len(ve2) == 4:
            b2 = b2.makeFillet(bar_w * 0.45, ve2)
        b2.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), -45)
        
        x_solid = b1.fuse(b2)
        x_solid.translate(FreeCAD.Vector(cx, cy, z_base))
        return x_solid

    def make_raised_stitches(x1, y1, x2, y2, n_stitches, stitch_len, line_w, h, z_base):
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx**2 + dy**2)
        angle = math.degrees(math.atan2(dy, dx))
        
        # Main scar bead
        seam = Part.makeBox(dist, line_w, h * 0.8)
        seam.translate(FreeCAD.Vector(0, -line_w/2.0, 0))
        seam.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), angle)
        seam.translate(FreeCAD.Vector(x1, y1, z_base))
        
        solids = [seam]
        sl2 = stitch_len / 2.0
        for i in range(1, n_stitches + 1):
            t = i / float(n_stitches + 1)
            cx = x1 + dx * t
            cy = y1 + dy * t
            # Pill-shaped cross stitch
            st = Part.makeBox(line_w * 1.3, stitch_len, h)
            st.translate(FreeCAD.Vector(-line_w * 0.65, -sl2, 0))
            # Fillet the ends
            ves = [e for e in st.Edges if abs(e.Length - h) < 0.01 and (abs(e.Vertexes[0].Point.y - sl2) < 0.01 or abs(e.Vertexes[0].Point.y + sl2) < 0.01)]
            if len(ves) == 4:
                try:
                    st = st.makeFillet(line_w * 0.5, ves)
                except Exception:
                    pass
            st.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), angle)
            st.translate(FreeCAD.Vector(cx, cy, z_base))
            solids.append(st)
            
        res = solids[0]
        for s in solids[1:]:
            res = res.fuse(s)
        return res

    def make_broken_heart(cx, cy, size, h, z_base):
        s2 = size / 2.0
        pts_left = [
            FreeCAD.Vector(-0.15, s2 * 0.40, 0),
            FreeCAD.Vector(-s2 * 0.50, s2 * 0.95, 0),
            FreeCAD.Vector(-s2 * 0.95, s2 * 0.45, 0),
            FreeCAD.Vector(-s2 * 0.70, -s2 * 0.20, 0),
            FreeCAD.Vector(-0.15, -s2 * 0.90, 0),
            FreeCAD.Vector(-0.40, -s2 * 0.40, 0),
            FreeCAD.Vector(-0.10, -s2 * 0.05, 0),
            FreeCAD.Vector(-0.35, s2 * 0.20, 0),
            FreeCAD.Vector(-0.15, s2 * 0.40, 0)
        ]
        s_l = Part.Face(Part.Wire(Part.makePolygon(pts_left))).extrude(FreeCAD.Vector(0, 0, h))
        
        pts_right = [
            FreeCAD.Vector(0.15, s2 * 0.40 + 0.15, 0),
            FreeCAD.Vector(0.35, s2 * 0.20 + 0.15, 0),
            FreeCAD.Vector(0.10, -s2 * 0.05 + 0.15, 0),
            FreeCAD.Vector(0.40, -s2 * 0.40 + 0.15, 0),
            FreeCAD.Vector(0.15, -s2 * 0.90 + 0.15, 0),
            FreeCAD.Vector(s2 * 0.70, -s2 * 0.20 + 0.15, 0),
            FreeCAD.Vector(s2 * 0.95, s2 * 0.45 + 0.15, 0),
            FreeCAD.Vector(s2 * 0.50, s2 * 0.95 + 0.15, 0),
            FreeCAD.Vector(0.15, s2 * 0.40 + 0.15, 0)
        ]
        s_r = Part.Face(Part.Wire(Part.makePolygon(pts_right))).extrude(FreeCAD.Vector(0, 0, h))
        heart = s_l.fuse(s_r)
        heart.translate(FreeCAD.Vector(cx, cy, z_base))
        return heart

    # -------------------------------------------------------------
    # 6. BUILD BOTTOM HALF
    # -------------------------------------------------------------
    h_bottom = 4.3
    face_bottom = make_coffin_polygon()
    solid_bottom = face_bottom.extrude(FreeCAD.Vector(0, 0, h_bottom))

    vert_edges = [e for e in solid_bottom.Edges if abs(e.Length - h_bottom) < 0.01]
    solid_bottom = solid_bottom.makeFillet(1.4, vert_edges)

    bot_edges = [e for e in solid_bottom.Edges if abs(e.Vertexes[0].Point.z) < 0.01 and abs(e.Vertexes[1].Point.z) < 0.01]
    solid_bottom = solid_bottom.makeFillet(1.0, bot_edges)

    cavity_w = 21.7
    cavity_l = 51.7
    cavity_y_start = 1.8
    floor_thk = 1.5

    inner_cavity = Part.makeBox(cavity_w, cavity_l, h_bottom - floor_thk + 0.1)
    inner_cavity.translate(FreeCAD.Vector(-cavity_w/2.0, cavity_y_start, floor_thk))
    bottom_shell = solid_bottom.cut(inner_cavity)

    # 4 Corner ledges
    ledge_size = 3.2
    ledge_h = 1.2
    ledges = [
        Part.makeBox(ledge_size, ledge_size, ledge_h),
        Part.makeBox(ledge_size, ledge_size, ledge_h),
        Part.makeBox(ledge_size, ledge_size, ledge_h),
        Part.makeBox(ledge_size, ledge_size, ledge_h)
    ]
    ledges[0].translate(FreeCAD.Vector(-cavity_w/2.0, cavity_y_start, floor_thk))
    ledges[1].translate(FreeCAD.Vector(cavity_w/2.0 - ledge_size, cavity_y_start, floor_thk))
    ledges[2].translate(FreeCAD.Vector(-cavity_w/2.0, cavity_y_start + cavity_l - ledge_size, floor_thk))
    ledges[3].translate(FreeCAD.Vector(cavity_w/2.0 - ledge_size, cavity_y_start + cavity_l - ledge_size, floor_thk))
    for l in ledges:
        bottom_shell = bottom_shell.fuse(l)

    # Catch slots
    snap_w = 4.2
    snap_h = 1.0
    snap_depth = 0.55
    snap_y1 = cavity_y_start + 12.0
    snap_y2 = cavity_y_start + cavity_l - 12.0
    snap_z = h_bottom - 0.6 - snap_h

    s_left1 = Part.makeBox(snap_depth + 0.1, snap_w, snap_h)
    s_left1.translate(FreeCAD.Vector(-cavity_w/2.0 - snap_depth, snap_y1 - snap_w/2.0, snap_z))
    s_left2 = Part.makeBox(snap_depth + 0.1, snap_w, snap_h)
    s_left2.translate(FreeCAD.Vector(-cavity_w/2.0 - snap_depth, snap_y2 - snap_w/2.0, snap_z))

    s_right1 = Part.makeBox(snap_depth + 0.1, snap_w, snap_h)
    s_right1.translate(FreeCAD.Vector(cavity_w/2.0 - 0.1, snap_y1 - snap_w/2.0, snap_z))
    s_right2 = Part.makeBox(snap_depth + 0.1, snap_w, snap_h)
    s_right2.translate(FreeCAD.Vector(cavity_w/2.0 - 0.1, snap_y2 - snap_w/2.0, snap_z))

    bottom_shell = bottom_shell.cut(s_left1).cut(s_left2).cut(s_right1).cut(s_right2)

    # USB cutter
    usb_cutter_b = make_microusb_cutter(h_bottom)
    bottom_shell = bottom_shell.cut(usb_cutter_b)

    # Flank Grip Flutes on bottom
    flute_depth = 0.45
    flute_w = 1.2
    flutes_bottom = []
    for i in range(5):
        y_pos = 22.0 + i * 2.2
        fl_l = Part.makeBox(flute_depth + 1.0, flute_w, h_bottom - 1.0 + 0.1)
        fl_l.translate(FreeCAD.Vector(-15.5, y_pos, 1.0))
        fl_r = Part.makeBox(flute_depth + 1.0, flute_w, h_bottom - 1.0 + 0.1)
        fl_r.translate(FreeCAD.Vector(14.5 - flute_depth, y_pos, 1.0))
        flutes_bottom.extend([fl_l, fl_r])
    for f in flutes_bottom:
        bottom_shell = bottom_shell.cut(f)

    # Backplate styling on bottom shell: Twin Bat Wings & Slime Drip
    back_bat = make_bat_crest(0, 25.0, 14.0, 5.8, 0.35, -0.35)
    # Deboss / cut into bottom face:
    bottom_shell = bottom_shell.cut(back_bat)

    # -------------------------------------------------------------
    # 7. BUILD TOP HALF
    # -------------------------------------------------------------
    h_top = 4.3
    face_top = make_coffin_polygon()
    solid_top = face_top.extrude(FreeCAD.Vector(0, 0, h_top))

    vert_edges_top = [e for e in solid_top.Edges if abs(e.Length - h_top) < 0.01]
    solid_top = solid_top.makeFillet(1.4, vert_edges_top)

    top_edges = [e for e in solid_top.Edges if abs(e.Vertexes[0].Point.z - h_top) < 0.01 and abs(e.Vertexes[1].Point.z - h_top) < 0.01]
    solid_top = solid_top.makeFillet(1.0, top_edges)

    roof_thk = 1.5
    inner_cavity_top = Part.makeBox(cavity_w, cavity_l, h_top - roof_thk + 0.1)
    inner_cavity_top.translate(FreeCAD.Vector(-cavity_w/2.0, cavity_y_start, -0.05))
    top_shell = solid_top.cut(inner_cavity_top)

    usb_cutter_t = make_microusb_cutter(0.0)
    top_shell = top_shell.cut(usb_cutter_t)

    # BOOTSEL & LED Dish Wells
    boot_x = -3.50
    boot_y = cavity_y_start + 39.00  # 40.80 mm
    led_x = -5.71
    led_y = cavity_y_start + 46.19   # 47.99 mm

    boot_well = make_revolved_well(0.9, 2.0, 0.55, 0.35, h_top)
    boot_well.translate(FreeCAD.Vector(boot_x, boot_y, 0))

    led_well = make_revolved_well(0.7, 1.4, 0.40, 0.30, h_top)
    led_well.translate(FreeCAD.Vector(led_x, led_y, 0))

    top_shell = top_shell.cut(boot_well).cut(led_well)

    led_ring = Part.makeCylinder(2.3, 0.2).cut(Part.makeCylinder(1.8, 0.3))
    led_ring.translate(FreeCAD.Vector(led_x, led_y, h_top - 0.15))

    boot_ring = Part.makeCylinder(2.8, 0.2).cut(Part.makeCylinder(2.4, 0.3))
    boot_ring.translate(FreeCAD.Vector(boot_x, boot_y, h_top - 0.15))

    top_shell = top_shell.cut(led_ring).cut(boot_ring)

    # Cantilever Snap Clips
    snap_tol = 0.20
    tab_w = 4.0
    tab_thk = 1.0
    hook_proj = 0.45
    z_root = 3.5
    z_catch = -0.7
    z_barb = -1.2
    z_tip = -2.4
    z_ceil = h_top - roof_thk

    x_wall_l = -cavity_w / 2.0
    pts_left = [
        FreeCAD.Vector(x_wall_l, 0, z_ceil),
        FreeCAD.Vector(x_wall_l, 0, z_root),
        FreeCAD.Vector(x_wall_l + snap_tol + tab_thk, 0, z_root),
        FreeCAD.Vector(x_wall_l + snap_tol + tab_thk, 0, z_barb + 0.6),
        FreeCAD.Vector(x_wall_l + snap_tol + tab_thk/2.0, 0, z_tip),
        FreeCAD.Vector(x_wall_l + snap_tol - hook_proj, 0, z_barb),
        FreeCAD.Vector(x_wall_l + snap_tol - hook_proj, 0, z_catch),
        FreeCAD.Vector(x_wall_l + snap_tol, 0, z_catch),
        FreeCAD.Vector(x_wall_l + snap_tol, 0, z_ceil),
        FreeCAD.Vector(x_wall_l, 0, z_ceil)
    ]
    tab_proto_l = Part.Face(Part.Wire(Part.makePolygon(pts_left))).extrude(FreeCAD.Vector(0, tab_w, 0))

    x_wall_r = cavity_w / 2.0
    pts_right = [
        FreeCAD.Vector(x_wall_r, 0, z_ceil),
        FreeCAD.Vector(x_wall_r, 0, z_root),
        FreeCAD.Vector(x_wall_r - snap_tol - tab_thk, 0, z_root),
        FreeCAD.Vector(x_wall_r - snap_tol - tab_thk, 0, z_barb + 0.6),
        FreeCAD.Vector(x_wall_r - snap_tol - tab_thk/2.0, 0, z_tip),
        FreeCAD.Vector(x_wall_r - snap_tol + hook_proj, 0, z_barb),
        FreeCAD.Vector(x_wall_r - snap_tol + hook_proj, 0, z_catch),
        FreeCAD.Vector(x_wall_r - snap_tol, 0, z_catch),
        FreeCAD.Vector(x_wall_r - snap_tol, 0, z_ceil),
        FreeCAD.Vector(x_wall_r, 0, z_ceil)
    ]
    tab_proto_r = Part.Face(Part.Wire(Part.makePolygon(pts_right))).extrude(FreeCAD.Vector(0, tab_w, 0))

    t_l1 = tab_proto_l.copy()
    t_l1.translate(FreeCAD.Vector(0, snap_y1 - tab_w/2.0, 0))
    t_l2 = tab_proto_l.copy()
    t_l2.translate(FreeCAD.Vector(0, snap_y2 - tab_w/2.0, 0))

    t_r1 = tab_proto_r.copy()
    t_r1.translate(FreeCAD.Vector(0, snap_y1 - tab_w/2.0, 0))
    t_r2 = tab_proto_r.copy()
    t_r2.translate(FreeCAD.Vector(0, snap_y2 - tab_w/2.0, 0))

    top_shell = top_shell.fuse(t_l1).fuse(t_l2).fuse(t_r1).fuse(t_r2)

    # Flank Grip Flutes on top
    flutes_top = []
    for i in range(5):
        y_pos = 22.0 + i * 2.2
        fl_l = Part.makeBox(flute_depth + 1.0, flute_w, h_top - 1.0 + 0.1)
        fl_l.translate(FreeCAD.Vector(-15.5, y_pos, -0.05))
        fl_r = Part.makeBox(flute_depth + 1.0, flute_w, h_top - 1.0 + 0.1)
        fl_r.translate(FreeCAD.Vector(14.5 - flute_depth, y_pos, -0.05))
        flutes_top.extend([fl_l, fl_r])
    for f in flutes_top:
        top_shell = top_shell.cut(f)

    # -------------------------------------------------------------
    # 8. TOP DECK GOTHIC RELIEFS: DRIPPING SLIME, CREST, STITCHES, X-PATCH, HEART
    # -------------------------------------------------------------
    # A. 3D Dripping Slime Drape (embossed +0.42 mm proud)
    drip_solid = make_drip_solid(h_top, 0.42)
    # Cut dish clearances through drip layer so BOOTSEL and LED stay cleanly accessible
    dish_clear_boot = Part.makeCylinder(2.9, 0.6)
    dish_clear_boot.translate(FreeCAD.Vector(boot_x, boot_y, h_top - 0.1))
    dish_clear_led = Part.makeCylinder(2.4, 0.6)
    dish_clear_led.translate(FreeCAD.Vector(led_x, led_y, h_top - 0.1))
    drip_solid = drip_solid.cut(dish_clear_boot).cut(dish_clear_led)

    top_shell = top_shell.fuse(drip_solid)

    # B. Royal Bat Crest (centered at X=0, Y=32.5, +0.38 mm proud)
    bat_crest = make_bat_crest(0, 32.5, 13.0, 5.4, 0.38, h_top)
    top_shell = top_shell.fuse(bat_crest)

    # C. "DEXTER" Typography
    font_file = "C:/Windows/Fonts/arialbd.ttf"
    if not os.path.exists(font_file):
        font_file = "C:/Windows/Fonts/arial.ttf"
    ss = Draft.make_shapestring(String="DEXTER", FontFile=font_file, Size=2.4)
    doc.recompute()
    bb_text = ss.Shape.BoundBox
    tw = bb_text.XMax - bb_text.XMin
    th = bb_text.YMax - bb_text.YMin
    text_solid = ss.Shape.extrude(FreeCAD.Vector(0, 0, 0.35))
    text_solid.translate(FreeCAD.Vector(-tw/2.0 - bb_text.XMin, 25.0 - th/2.0 - bb_text.YMin, h_top))
    top_shell = top_shell.fuse(text_solid)
    doc.removeObject(ss.Name)

    # D. Frankenstein Stitches (diagonal across mid-left deck, +0.40 mm proud)
    stitches = make_raised_stitches(-3.5, 14.5, -9.5, 19.5, 4, 3.2, 0.7, 0.40, h_top)
    top_shell = top_shell.fuse(stitches)

    # E. The Iconic "X" Patch / Bandage (lower-right deck, +0.40 mm proud)
    x_patch = make_x_patch(6.0, 10.5, 6.8, 1.8, 0.40, h_top)
    top_shell = top_shell.fuse(x_patch)

    # F. The Broken Heart (lower-left deck, +0.40 mm proud)
    broken_heart = make_broken_heart(-6.0, 9.5, 5.4, 0.40, h_top)
    top_shell = top_shell.fuse(broken_heart)

    print("Complete assembly built successfully!")
    print("Bottom shell volume:", bottom_shell.Volume, "Solids:", len(bottom_shell.Solids))
    print("Top shell volume:", top_shell.Volume, "Solids:", len(top_shell.Solids))

    # Add to document side-by-side
    obj_bottom = doc.addObject("Part::Feature", "Pico2W_Bottom_Half")
    obj_bottom.Shape = bottom_shell
    obj_bottom.Label = "Pico 2 W Case - Bottom Half (Gothic Coffin)"

    top_display = top_shell.copy()
    top_display.translate(FreeCAD.Vector(36.0, 0, 0))
    obj_top = doc.addObject("Part::Feature", "Pico2W_Top_Half")
    obj_top.Shape = top_display
    obj_top.Label = "Pico 2 W Case - Top Half (Gothic Imp Dexter Edition)"

    sky_blue = (0.53, 0.76, 0.94)
    obj_bottom.ViewObject.ShapeColor = sky_blue
    obj_top.ViewObject.ShapeColor = sky_blue

    doc.recompute()
    return doc

build_complete_case()
