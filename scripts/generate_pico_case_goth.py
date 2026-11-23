"""
Parametric Raspberry Pi Pico 2 W Snap-Fit Enclosure - Gothic Coffin Imp Edition
Dexter Controller Project - Personalized Holiday Gift Edition

Complete Overhaul with Clean Flat Coffin, 100% Flush Slime, Restored Broken Heart, and Sculpted Backplate:
1. 6-Sided Gothic Coffin Silhouette with Sculpted Bat Wings at shoulders.
2. Clean Flat Coffin Body (Zero rim bevel on coffin):
   - Coffin vertical sidewalls rise straight at 90 degrees with zero rim bevel.
   - Sits flush with the slime drape without any ledge, shelf, or overhang.
   - Vertical corners are filleted (R = 1.4 mm) for ergonomic pocket comfort.
3. 100% Flush Organic 3D Dripping Slime Drape:
   - Outer head and shoulder boundaries match the exact filleted coffin coordinates (R = 1.4 mm).
   - Outer top rim of the slime is beveled (R = 0.35 mm), curving smoothly into the flush sidewalls.
   - Drip droplet lobes stepping down onto the deck with soft rounded liquid fillets (R = 0.12 mm).
   - Detached liquid bead on right flank (R = 0.18 mm).
4. Restored Tilted Broken Heart:
   - Authentic broken heart with central jagged lightning crack.
   - Both halves present, fully beveled top edges (R = 0.11 mm).
   - Size 7.2 mm, tilted -16 degrees at (-5.8, 10.0).
5. Repositioned Bat Crest (centered at Y = 29.0 mm) with clean negative space below the slime.
6. Times New Roman Bold Gothic "DEXTER" Typography (repositioned at Y = 22.0 mm, individually beveled letters).
7. Repositioned Curved Frankenstein Stitches:
   - Sweeps from bottom center (X=1.0, Y=4.5) up to right flank (X=11.5, Y=19.5).
   - Main seam line is fully rounded and beveled (arched barrel profile).
   - 5 crossbars with hemispherical pill fillets and beveled rims.
8. X-Patch removed.
9. Protruding & Beveled Backplate on Bottom Shell:
   - Mirrored twin bat wings and cascading slime drape protrude outward on the bottom shell.
   - Bevels are applied directly to the outside visible surface (Z = -0.38 mm and -0.42 mm).
   - 100% flush with the outer sidewalls.
   - Monolithic solid body (Solids: 1).
10. Authentic Micro-USB trapezoidal lead-in port, camera-style concave dish wells, and monolithic snap clips.
"""

import os
import math
import FreeCAD
import Part
import Mesh
import Draft

def create_goth_enclosure(doc=None, export_files=True, output_dir=r"c:\Users\dwinslow\Documents\Dexter_Controller_Project\case_3d"):
    if doc is None:
        doc = FreeCAD.activeDocument()
        if doc is None or doc.Name != "pico2w_enclosure_goth":
            doc = FreeCAD.newDocument("pico2w_enclosure_goth")

    # Clean existing objects
    for obj_name in ["Pico2W_Bottom_Half", "Pico2W_Top_Half"]:
        if doc.getObject(obj_name):
            doc.removeObject(obj_name)

    # -------------------------------------------------------------
    # 1. PARAMETRIC DIMENSIONS
    # -------------------------------------------------------------
    pcb_len = 51.0
    pcb_wid = 21.0
    pcb_thk = 1.0
    pcb_clearance = 0.35
    
    cavity_len = pcb_len + 2 * pcb_clearance  # 51.7 mm
    cavity_wid = pcb_wid + 2 * pcb_clearance  # 21.7 mm
    
    cavity_y_start = 1.8  # Foot wall = 1.8 mm
    total_len = 56.0      # Head wall = 56.0 - 53.5 = 2.5 mm
    
    bottom_height = 4.3  # mm
    top_height = 4.3     # mm
    total_height = bottom_height + top_height  # 8.6 mm
    
    floor_thk = 1.5
    roof_thk = 1.5
    under_pcb_clearance = 1.2
    h_drip = 0.42

    # -------------------------------------------------------------
    # 2. 6-SIDED COFFIN WITH INTEGRATED SCULPTED BAT WINGS
    # -------------------------------------------------------------
    pts_coffin_r = [
        FreeCAD.Vector(0, 0, 0),
        FreeCAD.Vector(12.7, 0, 0),         # Foot corner (W = 25.4 mm)
        FreeCAD.Vector(14.5, 36.0, 0),      # Lower flank (W = 29.0 mm)
        FreeCAD.Vector(17.4, 41.5, 0),      # Primary bat wingtip flare (W = 34.8 mm)
        FreeCAD.Vector(15.2, 44.0, 0),      # Wing scallop notch (W = 30.4 mm)
        FreeCAD.Vector(16.2, 46.5, 0),      # Secondary winglet cusp (W = 32.4 mm)
        FreeCAD.Vector(14.0, 49.5, 0),      # Upper shoulder (W = 28.0 mm)
        FreeCAD.Vector(12.7, 56.0, 0),      # Head corner (W = 25.4 mm)
        FreeCAD.Vector(0, 56.0, 0),         # Head center
    ]
    pts_coffin_l = [FreeCAD.Vector(-p.x, p.y, 0) for p in reversed(pts_coffin_r[1:-1])]
    all_pts_coffin = pts_coffin_r + pts_coffin_l + [pts_coffin_r[0]]
    wire_coffin = Part.Wire(Part.makePolygon(all_pts_coffin))

    # -------------------------------------------------------------
    # 3. AUTHENTIC TRAPEZOIDAL MICRO-USB CUTTER
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
        
        w_outer = microusb_wire(10.8, 5.0, 1.3, total_len + 0.5)
        w_bevel = microusb_wire(8.0, 3.2, 0.85, total_len - 1.2)
        w_inner = microusb_wire(8.0, 3.2, 0.85, total_len - 4.0)
        cutter = Part.makeLoft([w_inner, w_bevel, w_outer], True)
        cutter.translate(FreeCAD.Vector(0, 0, z_center))
        return cutter

    # -------------------------------------------------------------
    # 4. CAMERA-STYLE CONCAVE WELL CUTTER
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
    # 5. 100% FLUSH BEVELED ORGANIC DRIPPING SLIME
    # -------------------------------------------------------------
    # Sliced directly from the coffin base solid extruded by h_drip
    # and filleted vertically by R = 1.4 mm, guaranteeing 100% identical corner curves!
    def make_clean_flush_slime():
        s_slime_base = Part.Face(wire_coffin).extrude(FreeCAD.Vector(0, 0, h_drip))
        ve_slime = [e for e in s_slime_base.Edges if abs(e.Length - h_drip) < 0.01]
        s_slime_base = s_slime_base.makeFillet(1.4, ve_slime)

        pts_cutter = [
            FreeCAD.Vector(25.0, -5.0, 0),
            FreeCAD.Vector(-25.0, -5.0, 0),
            FreeCAD.Vector(-25.0, 45.0, 0),
            FreeCAD.Vector(-18.0, 43.5, 0),
        ]
        def append_arc(cx, cy, r, a_start, a_end, n_steps=6):
            for i in range(n_steps + 1):
                t = i / float(n_steps)
                ang = math.radians(a_start + (a_end - a_start) * t)
                pts_cutter.append(FreeCAD.Vector(cx + r * math.cos(ang), cy + r * math.sin(ang), 0))

        # Organic Drip Boundary
        append_arc(-12.6, 41.2, 1.4, 180, 360, 6)
        append_arc(-9.8, 43.8, 1.5, 180, 0, 5)
        append_arc(-6.8, 41.0, 1.5, 180, 360, 6)
        append_arc(-3.8, 44.0, 1.5, 180, 0, 5)
        pts_cutter.append(FreeCAD.Vector(-1.6, 38.8, 0))
        append_arc(0.0, 37.6, 1.6, 160, 380, 8)
        pts_cutter.append(FreeCAD.Vector(1.6, 38.8, 0))
        append_arc(4.2, 44.5, 1.5, 180, 0, 5)
        append_arc(7.2, 41.5, 1.5, 180, 360, 6)
        append_arc(10.2, 43.5, 1.6, 180, 0, 5)
        append_arc(13.2, 40.8, 1.4, 180, 360, 6)

        pts_cutter.append(FreeCAD.Vector(18.0, 43.5, 0))
        pts_cutter.append(FreeCAD.Vector(25.0, 45.0, 0))
        pts_cutter.append(FreeCAD.Vector(25.0, -5.0, 0))

        w_cutter = Part.Wire(Part.makePolygon(pts_cutter))
        f_cutter = Part.Face(w_cutter).extrude(FreeCAD.Vector(0, 0, h_drip + 0.1))
        f_cutter.translate(FreeCAD.Vector(0, 0, -0.01))

        s_slime_clean = s_slime_base.cut(f_cutter)

        # Fillet the organic drip step edge
        top_e = [
            e for e in s_slime_clean.Edges
            if len(e.Vertexes) >= 2
            and abs(e.Vertexes[0].Point.z - h_drip) < 0.01 and abs(e.Vertexes[1].Point.z - h_drip) < 0.01
            and e.Vertexes[0].Point.y < 43.0 and e.Vertexes[1].Point.y < 43.0
        ]
        try:
            s_slime_clean = s_slime_clean.makeFillet(0.12, top_e)
        except Exception:
            pass

        # Detached liquid droplet bead on right flank
        drop_r = Part.makeCylinder(0.85, h_drip)
        top_d = [e for e in drop_r.Edges if len(e.Vertexes) >= 1 and abs(e.Vertexes[0].Point.z - h_drip) < 0.01]
        try:
            drop_r = drop_r.makeFillet(0.18, top_d)
        except Exception:
            pass
        drop_r.translate(FreeCAD.Vector(7.2, 37.0, 0))

        # Bevel the outer head and shoulder rim of the slime
        outer_rim_e = [
            e for e in s_slime_clean.Edges
            if len(e.Vertexes) >= 2
            and abs(e.Vertexes[0].Point.z - h_drip) < 0.01 and abs(e.Vertexes[1].Point.z - h_drip) < 0.01
            and (abs(e.Vertexes[0].Point.y - total_len) < 0.01 or (abs(e.Vertexes[0].Point.x) > 13.0 and e.Vertexes[0].Point.y > 45.0))
        ]
        try:
            s_slime_clean = s_slime_clean.makeFillet(0.35, outer_rim_e)
        except Exception:
            pass

        return s_slime_clean.fuse(drop_r)

    # -------------------------------------------------------------
    # 6. BEVELED GOTHIC MOTIFS (BAT CREST, STITCHES, BROKEN HEART)
    # -------------------------------------------------------------
    def make_beveled_bat_crest(cx, cy, w, h, depth):
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

        top_e = [
            e for e in s_bat.Edges
            if len(e.Vertexes) >= 1
            and abs(e.Vertexes[0].Point.z - depth) < 0.01
            and (len(e.Vertexes) < 2 or abs(e.Vertexes[1].Point.z - depth) < 0.01)
        ]
        try:
            s_bat = s_bat.makeFillet(0.08, top_e)
        except Exception:
            pass

        s_bat.translate(FreeCAD.Vector(cx, cy, 0))
        return s_bat

    def make_beveled_heart(cx, cy, size, h, tilt_deg, z_base):
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

        top_l = [
            e for e in s_l.Edges
            if len(e.Vertexes) >= 2
            and abs(e.Vertexes[0].Point.z - h) < 0.01 and abs(e.Vertexes[1].Point.z - h) < 0.01
        ]
        top_r = [
            e for e in s_r.Edges
            if len(e.Vertexes) >= 2
            and abs(e.Vertexes[0].Point.z - h) < 0.01 and abs(e.Vertexes[1].Point.z - h) < 0.01
        ]
        try:
            s_l = s_l.makeFillet(0.11, top_l)
            s_r = s_r.makeFillet(0.11, top_r)
        except Exception:
            pass

        heart = s_l.fuse(s_r)
        if tilt_deg != 0:
            heart.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), tilt_deg)
        heart.translate(FreeCAD.Vector(cx, cy, z_base))
        return heart

    def make_beveled_curved_stitches(p0, p_ctrl, p1, n_stitches, stitch_len, line_w, h, z_base):
        def bezier_pt(t):
            x = (1-t)**2 * p0[0] + 2*(1-t)*t * p_ctrl[0] + t**2 * p1[0]
            y = (1-t)**2 * p0[1] + 2*(1-t)*t * p_ctrl[1] + t**2 * p1[1]
            return x, y

        def bezier_tangent(t):
            dx = 2*(1-t)*(p_ctrl[0] - p0[0]) + 2*t*(p1[0] - p_ctrl[0])
            dy = 2*(1-t)*(p_ctrl[1] - p0[1]) + 2*t*(p1[1] - p_ctrl[1])
            mag = math.sqrt(dx**2 + dy**2)
            return dx/mag, dy/mag

        # Arched & beveled seam line
        n_seam_segs = 16
        pts_seam = [bezier_pt(i / float(n_seam_segs)) for i in range(n_seam_segs + 1)]
        seam_solids = []
        for i in range(n_seam_segs):
            x_a, y_a = pts_seam[i]
            x_b, y_b = pts_seam[i+1]
            dx = x_b - x_a
            dy = y_b - y_a
            d = math.sqrt(dx**2 + dy**2)
            ang = math.degrees(math.atan2(dy, dx))
            seg = Part.makeBox(d + 0.1, line_w, h * 0.8)
            seg.translate(FreeCAD.Vector(0, -line_w/2.0, 0))

            top_e_seg = [
                e for e in seg.Edges
                if abs(e.Length - (d + 0.1)) < 0.01
                and len(e.Vertexes) >= 1
                and abs(e.Vertexes[0].Point.z - h*0.8) < 0.01
            ]
            if len(top_e_seg) == 2:
                try:
                    seg = seg.makeFillet(line_w * 0.35, top_e_seg)
                except Exception:
                    pass

            seg.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), ang)
            seg.translate(FreeCAD.Vector(x_a, y_a, z_base))
            seam_solids.append(seg)

        full_seam = seam_solids[0]
        for s in seam_solids[1:]:
            full_seam = full_seam.fuse(s)

        # Crossbars with rounded pill ends and beveled top rim
        cross_solids = []
        sl2 = stitch_len / 2.0
        for i in range(1, n_stitches + 1):
            t = i / float(n_stitches + 1)
            cx, cy = bezier_pt(t)
            tx, ty = bezier_tangent(t)
            ang_tangent = math.degrees(math.atan2(ty, tx))
            ang_cross = ang_tangent + 90.0

            st = Part.makeBox(stitch_len, line_w * 1.35, h)
            st.translate(FreeCAD.Vector(-sl2, -line_w * 0.675, 0))
            ve = [
                e for e in st.Edges
                if abs(e.Length - h) < 0.01
                and len(e.Vertexes) >= 1
                and (abs(e.Vertexes[0].Point.x - sl2) < 0.01 or abs(e.Vertexes[0].Point.x + sl2) < 0.01)
            ]
            if len(ve) == 4:
                try:
                    st = st.makeFillet(line_w * 0.55, ve)
                except Exception:
                    pass
            top_e = [
                e for e in st.Edges
                if len(e.Vertexes) >= 2
                and abs(e.Vertexes[0].Point.z - h) < 0.01 and abs(e.Vertexes[1].Point.z - h) < 0.01
            ]
            try:
                st = st.makeFillet(0.08, top_e)
            except Exception:
                pass

            st.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), ang_cross)
            st.translate(FreeCAD.Vector(cx, cy, z_base))
            cross_solids.append(st)

        res = full_seam
        for s in cross_solids:
            res = res.fuse(s)
        return res

    # -------------------------------------------------------------
    # 7. BUILD BOTTOM HALF (CLEAN FLAT COFFIN BODY + PROTRUDING BACKPLATE)
    # -------------------------------------------------------------
    solid_bottom = Part.Face(wire_coffin).extrude(FreeCAD.Vector(0, 0, bottom_height))
    vert_edges = [e for e in solid_bottom.Edges if abs(e.Length - bottom_height) < 0.01]
    solid_bottom = solid_bottom.makeFillet(1.4, vert_edges)
    # Coffin piece has clean vertical sidewalls at 90 degrees with zero rim bevel

    inner_cavity = Part.makeBox(cavity_wid, cavity_len, bottom_height - floor_thk + 0.1)
    inner_cavity.translate(FreeCAD.Vector(-cavity_wid/2.0, cavity_y_start, floor_thk))
    bottom_shell = solid_bottom.cut(inner_cavity)

    # 4 Corner PCB rest ledges with integrated M2 Locating Nubs
    ledge_x = 5.8
    ledge_y = 4.0
    ledge_h = under_pcb_clearance + 0.1
    ledges = [
        Part.makeBox(ledge_x + 0.5, ledge_y + 0.5, ledge_h),
        Part.makeBox(ledge_x + 0.5, ledge_y + 0.5, ledge_h),
        Part.makeBox(ledge_x + 0.5, ledge_y + 0.5, ledge_h),
        Part.makeBox(ledge_x + 0.5, ledge_y + 0.5, ledge_h)
    ]
    ledges[0].translate(FreeCAD.Vector(-cavity_wid/2.0 - 0.5, cavity_y_start - 0.5, floor_thk - 0.1))
    ledges[1].translate(FreeCAD.Vector(cavity_wid/2.0 - ledge_x, cavity_y_start - 0.5, floor_thk - 0.1))
    ledges[2].translate(FreeCAD.Vector(-cavity_wid/2.0 - 0.5, cavity_y_start + cavity_len - ledge_y, floor_thk - 0.1))
    ledges[3].translate(FreeCAD.Vector(cavity_wid/2.0 - ledge_x, cavity_y_start + cavity_len - ledge_y, floor_thk - 0.1))
    for l in ledges:
        bottom_shell = bottom_shell.fuse(l)

    # 4 Locating Nubs locking into the Pico 2 W M2 mounting holes (Ø1.8 mm into Ø2.1 mm holes)
    nub_r = 0.90
    nub_h = 0.95
    nubs = [
        Part.makeCylinder(nub_r, nub_h),
        Part.makeCylinder(nub_r, nub_h),
        Part.makeCylinder(nub_r, nub_h),
        Part.makeCylinder(nub_r, nub_h)
    ]
    z_nub = floor_thk + under_pcb_clearance - 0.1
    nubs[0].translate(FreeCAD.Vector(-5.7, cavity_y_start + 2.0, z_nub))
    nubs[1].translate(FreeCAD.Vector(5.7, cavity_y_start + 2.0, z_nub))
    nubs[2].translate(FreeCAD.Vector(-5.7, cavity_y_start + 49.0, z_nub))
    nubs[3].translate(FreeCAD.Vector(5.7, cavity_y_start + 49.0, z_nub))
    for n in nubs:
        bottom_shell = bottom_shell.fuse(n)

    # Solid Cylindrical Alignment Pins in Bat Wings (Ø2.3 mm with 45-deg lead-in chamfer)
    pin_r = 1.15
    pin_h = 1.9
    pin_embed = 0.2
    pin_l = Part.makeCylinder(pin_r, pin_h + pin_embed).fuse(Part.makeCone(pin_r, 0.6, 0.4).translate(FreeCAD.Vector(0,0,pin_h + pin_embed)))
    pin_r_wing = Part.makeCylinder(pin_r, pin_h + pin_embed).fuse(Part.makeCone(pin_r, 0.6, 0.4).translate(FreeCAD.Vector(0,0,pin_h + pin_embed)))
    pin_l.translate(FreeCAD.Vector(-13.8, 41.5, bottom_height - pin_embed))
    pin_r_wing.translate(FreeCAD.Vector(13.8, 41.5, bottom_height - pin_embed))
    bottom_shell = bottom_shell.fuse(pin_l).fuse(pin_r_wing)

    # 3-Sided Stepped Interlocking Alignment Tongue (Left, Right, Head)
    tongue_h = 0.90
    tongue_thk = 0.75
    tongue_clr = 0.18 # SLA resin clearance
    t_left = Part.makeBox(tongue_thk + 0.2, cavity_len - 3.5, tongue_h + pin_embed)
    t_left.translate(FreeCAD.Vector(-cavity_wid/2.0 + tongue_clr - 0.2, cavity_y_start + 3.5, bottom_height - pin_embed))
    t_right = Part.makeBox(tongue_thk + 0.2, cavity_len - 3.5, tongue_h + pin_embed)
    t_right.translate(FreeCAD.Vector(cavity_wid/2.0 - tongue_clr - tongue_thk, cavity_y_start + 3.5, bottom_height - pin_embed))
    t_head = Part.makeBox(cavity_wid - 2.0, tongue_thk + 0.2, tongue_h + pin_embed)
    t_head.translate(FreeCAD.Vector(-cavity_wid/2.0 + 1.0, cavity_y_start + cavity_len - tongue_clr - tongue_thk, bottom_height - pin_embed))
    bottom_shell = bottom_shell.fuse(t_left).fuse(t_right).fuse(t_head)

    # Cut Micro-USB port
    usb_cutter_b = make_microusb_cutter(bottom_height)
    bottom_shell = bottom_shell.cut(usb_cutter_b)

    # Flank Grip Flutes (connecting seamlessly across parting seam)
    flute_depth = 0.45
    flute_w = 1.2
    flutes_bottom = []
    for i in range(5):
        y_pos = 22.0 + i * 2.2
        fl_l = Part.makeBox(flute_depth + 1.0, flute_w, bottom_height - 1.0 + 0.1)
        fl_l.translate(FreeCAD.Vector(-15.5, y_pos, 1.0))
        fl_r = Part.makeBox(flute_depth + 1.0, flute_w, bottom_height - 1.0 + 0.1)
        fl_r.translate(FreeCAD.Vector(14.5 - flute_depth, y_pos, 1.0))
        flutes_bottom.extend([fl_l, fl_r])
    for f in flutes_bottom:
        bottom_shell = bottom_shell.cut(f)

    # PROTRUDING & BEVELED BACKPLATE RELIEFS (MIRRORED ACROSS XY PLANE SO BEVEL FACES OUTWARD)
    # 1. Backplate Cascading Slime (100% flush with outer sidewalls, matching R = 1.4 mm corner curves)
    back_slime = make_clean_flush_slime()
    back_slime_m = back_slime.mirror(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1))
    bottom_shell = bottom_shell.fuse(back_slime_m)

    # 2. Backplate Twin Bat Wings (+0.38 mm proud, bevel on the visible face)
    back_bat = make_beveled_bat_crest(0, 26.0, 15.0, 6.2, 0.38)
    back_bat_m = back_bat.mirror(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1))
    bottom_shell = bottom_shell.fuse(back_bat_m)

    # -------------------------------------------------------------
    # 8. BUILD TOP HALF (CLEAN FLAT COFFIN BODY)
    # -------------------------------------------------------------
    solid_top = Part.Face(wire_coffin).extrude(FreeCAD.Vector(0, 0, top_height))
    vert_edges_top = [e for e in solid_top.Edges if abs(e.Length - top_height) < 0.01]
    solid_top = solid_top.makeFillet(1.4, vert_edges_top)
    # Coffin piece has clean vertical sidewalls at 90 degrees with zero rim bevel

    inner_cavity_top = Part.makeBox(cavity_wid, cavity_len, top_height - roof_thk + 0.1)
    inner_cavity_top.translate(FreeCAD.Vector(-cavity_wid/2.0, cavity_y_start, -0.05))
    top_shell = solid_top.cut(inner_cavity_top)

    usb_cutter_t = make_microusb_cutter(0.0)
    top_shell = top_shell.cut(usb_cutter_t)

    # Camera-Style Concave Well Cutters for BOOTSEL & LED
    boot_x = -3.50
    boot_y = cavity_y_start + 39.00  # 40.80 mm
    led_x = -5.71
    led_y = cavity_y_start + 46.19   # 47.99 mm

    boot_well = make_revolved_well(0.9, 2.0, 0.55, 0.35, top_height)
    boot_well.translate(FreeCAD.Vector(boot_x, boot_y, 0))

    led_well = make_revolved_well(0.7, 1.4, 0.40, 0.30, top_height)
    led_well.translate(FreeCAD.Vector(led_x, led_y, 0))

    top_shell = top_shell.cut(boot_well).cut(led_well)

    led_ring = Part.makeCylinder(2.3, 0.2).cut(Part.makeCylinder(1.8, 0.3))
    led_ring.translate(FreeCAD.Vector(led_x, led_y, top_height - 0.15))

    boot_ring = Part.makeCylinder(2.8, 0.2).cut(Part.makeCylinder(2.4, 0.3))
    boot_ring.translate(FreeCAD.Vector(boot_x, boot_y, top_height - 0.15))

    top_shell = top_shell.cut(led_ring).cut(boot_ring)

    # Alignment Sockets in Bat Wings (Ø2.7 mm, depth 2.4 mm, giving 0.20 mm radial clearance for pins)
    socket_r = 1.35
    socket_h = 2.4
    sock_l = Part.makeCylinder(socket_r, socket_h)
    sock_r = Part.makeCylinder(socket_r, socket_h)
    sock_l.translate(FreeCAD.Vector(-13.8, 41.5, -0.01))
    sock_r.translate(FreeCAD.Vector(13.8, 41.5, -0.01))
    top_shell = top_shell.cut(sock_l).cut(sock_r)

    # Flank Grip Flutes on top
    flutes_top = []
    for i in range(5):
        y_pos = 22.0 + i * 2.2
        fl_l = Part.makeBox(flute_depth + 1.0, flute_w, top_height - 1.0 + 0.1)
        fl_l.translate(FreeCAD.Vector(-15.5, y_pos, -0.05))
        fl_r = Part.makeBox(flute_depth + 1.0, flute_w, top_height - 1.0 + 0.1)
        fl_r.translate(FreeCAD.Vector(14.5 - flute_depth, y_pos, -0.05))
        flutes_top.extend([fl_l, fl_r])
    for f in flutes_top:
        top_shell = top_shell.cut(f)

    # -------------------------------------------------------------
    # 9. FRONT DECK GOTHIC MOTIFS (BEVELED 3D RELIEFS)
    # -------------------------------------------------------------
    # A. 100% Flush 3D Dripping Slime Drape (Zero Overhang, Matching R = 1.4 mm Corner Arcs)
    drip_solid = make_clean_flush_slime()
    drip_solid.translate(FreeCAD.Vector(0, 0, top_height))
    dish_clear_boot = Part.makeCylinder(2.9, 0.6)
    dish_clear_boot.translate(FreeCAD.Vector(boot_x, boot_y, top_height - 0.1))
    dish_clear_led = Part.makeCylinder(2.4, 0.6)
    dish_clear_led.translate(FreeCAD.Vector(led_x, led_y, top_height - 0.1))
    drip_solid = drip_solid.cut(dish_clear_boot).cut(dish_clear_led)

    top_shell = top_shell.fuse(drip_solid)

    # B. Royal Bat Crest (Moved to Y = 29.0 mm, beveled edges, +0.38 mm proud)
    bat_crest = make_beveled_bat_crest(0, 29.0, 13.5, 5.6, 0.38)
    bat_crest.translate(FreeCAD.Vector(0, 0, top_height))
    top_shell = top_shell.fuse(bat_crest)

    # C. "DEXTER" Typography (Times New Roman Bold, moved to Y = 22.0 mm, individually beveled letters)
    font_file = "C:/Windows/Fonts/timesbd.ttf"
    if not os.path.exists(font_file):
        font_file = "C:/Windows/Fonts/times.ttf"
    if not os.path.exists(font_file):
        font_file = "C:/Windows/Fonts/georgiab.ttf"

    ss = Draft.make_shapestring(String="DEXTER", FontFile=font_file, Size=2.4)
    doc.recompute()
    text_shape = ss.Shape.copy()
    doc.removeObject(ss.Name)

    bb_text = text_shape.BoundBox
    tw = bb_text.XMax - bb_text.XMin
    th = bb_text.YMax - bb_text.YMin

    beveled_letters = []
    for f in text_shape.Faces:
        s = f.extrude(FreeCAD.Vector(0, 0, 0.35))
        top_edges = [e for e in s.Edges if len(e.Vertexes) >= 1 and abs(e.Vertexes[0].Point.z - 0.35) < 0.01]
        try:
            s = s.makeFillet(0.05, top_edges)
        except Exception:
            pass
        beveled_letters.append(s)

    full_beveled_text = beveled_letters[0]
    for letter in beveled_letters[1:]:
        full_beveled_text = full_beveled_text.fuse(letter)

    full_beveled_text.translate(FreeCAD.Vector(-tw/2.0 - bb_text.XMin, 22.0 - th/2.0 - bb_text.YMin, top_height))
    top_shell = top_shell.fuse(full_beveled_text)

    # D. Repositioned Curved Frankenstein Stitches (Arched & Beveled Seam Line + Pill Crossbars)
    stitches = make_beveled_curved_stitches((1.0, 4.5), (5.5, 11.5), (11.5, 19.5), 5, 4.2, 0.85, 0.42, top_height)
    top_shell = top_shell.fuse(stitches)

    # E. Restored Authentic Broken Heart (Both Halves, Lightning Crack, Beveled, Tilted -16 deg)
    broken_heart = make_beveled_heart(-5.8, 10.0, 7.2, 0.42, -16.0, top_height)
    top_shell = top_shell.fuse(broken_heart)

    print("Complete assembly built successfully!")
    print(f"Bottom shell volume: {bottom_shell.Volume:.2f} mm3, Solids: {len(bottom_shell.Solids)}")
    print(f"Top shell volume: {top_shell.Volume:.2f} mm3, Solids: {len(top_shell.Solids)}")

    # -------------------------------------------------------------
    # 10. ADD OBJECTS TO ACTIVE FREECAD DOCUMENT (SIDE-BY-SIDE DISPLAY)
    # -------------------------------------------------------------
    obj_bottom = doc.addObject("Part::Feature", "Pico2W_Bottom_Half")
    obj_bottom.Shape = bottom_shell
    obj_bottom.Label = "Pico 2 W Case - Bottom Half (Gothic Coffin)"

    top_display = top_shell.copy()
    top_display.translate(FreeCAD.Vector(38.0, 0, 0))
    obj_top = doc.addObject("Part::Feature", "Pico2W_Top_Half")
    obj_top.Shape = top_display
    obj_top.Label = "Pico 2 W Case - Top Half (Gothic Imp Dexter Edition)"

    try:
        sky_blue = (0.53, 0.76, 0.94)
        obj_bottom.ViewObject.ShapeColor = sky_blue
        obj_top.ViewObject.ShapeColor = sky_blue
    except Exception:
        pass

    doc.recompute()

    # -------------------------------------------------------------
    # 11. EXPORT STEP / STL / FCStd FILES
    # -------------------------------------------------------------
    if export_files:
        os.makedirs(output_dir, exist_ok=True)
        fcstd_path = os.path.join(output_dir, "pico2w_enclosure-goth.FCStd")
        doc.saveAs(os.path.abspath(fcstd_path))

        step_bottom = os.path.join(output_dir, "pico2w_case_bottom_goth.step")
        step_top = os.path.join(output_dir, "pico2w_case_top_goth.step")
        bottom_shell.exportStep(os.path.abspath(step_bottom))
        top_shell.exportStep(os.path.abspath(step_top))

        stl_bottom = os.path.join(output_dir, "pico2w_case_bottom_goth.stl")
        stl_top = os.path.join(output_dir, "pico2w_case_top_goth.stl")

        mesh_bottom = Mesh.Mesh()
        mesh_bottom.addFacets(bottom_shell.tessellate(0.05))
        mesh_bottom.write(os.path.abspath(stl_bottom))

        mesh_top = Mesh.Mesh()
        mesh_top.addFacets(top_shell.tessellate(0.05))
        mesh_top.write(os.path.abspath(stl_top))

        print(f"Files exported to {output_dir}")

    return doc

# Execute directly so running script runs the overhaul
create_goth_enclosure()
