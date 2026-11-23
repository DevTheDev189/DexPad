"""
Parametric Raspberry Pi Pico 2 W Enclosure for FreeCAD
DexPad Project - Modern Minimalist Dongle Enclosure

Features:
- Sub-millimeter fit verified directly against official Pico W 3D CAD model.
- Exact hole positions at (4.8mm, 2.0mm) and (4.8mm, 49.0mm) matching RP2040 / RP2350 PCB mounting holes.
- 4 solid corner alignment friction pegs (1.9mm dia with 45-deg lead-in chamfer) passing cleanly through PCB holes into top shell sockets.
- ZERO cantilever clips and ZERO outer wall catch holes (clean solid unblemished exterior).
- Generous internal headroom (6.2 mm cavity height) to house the USB port, Wi-Fi RF shield can, and passives.
- Authentic trapezoidal Micro-USB lead-in funnel on the rear port.
- Rounded S-curve concave dished wells for BOOTSEL pinhole and Status LED.
- Iconic DexPad logo debossed on the top deck with stepped 3D overlap:
  - Top contoured crossing stroke: MORE RECESSED (0.55 mm deep)
  - Lower 45-degree capsule: LESS RECESSED (0.25 mm deep)
"""

import os
import math
import FreeCAD
import Part
import Mesh

def create_enclosure(doc=None, export_files=True, output_dir=r"c:\Users\dwinslow\Documents\Dexter_Controller_Project\case_3d"):
    if doc is None:
        doc = FreeCAD.activeDocument()
        if doc is None:
            doc = FreeCAD.newDocument("pico2w_enclosure")

    # Clean existing objects if re-running in active doc
    for obj_name in ["Pico2W_Bottom_Half", "Pico2W_Top_Half"]:
        if doc.getObject(obj_name):
            doc.removeObject(obj_name)

    # -------------------------------------------------------------
    # PARAMETRIC DIMENSIONS (in mm)
    # Verified against PicoW.stp: PCB is 21.0 x 51.0 x 1.0 mm
    # With USB overhang, total board length is 52.35 mm
    # -------------------------------------------------------------
    pcb_len = 51.0
    pcb_wid = 21.0
    pcb_thk = 1.0
    pcb_clearance = 0.45  # per side (0.9 mm total)

    cavity_len = 53.4     # Accommodates 51.0mm PCB + 1.35mm USB connector + clearance
    cavity_wid = pcb_wid + 2 * pcb_clearance  # 21.9 mm

    wall_thk = 1.6
    floor_thk = 1.4
    roof_thk = 1.4
    corner_rad = 2.5
    edge_fillet_rad = 1.2

    # Overall Dimensions
    outer_len = cavity_len + 2 * wall_thk  # 56.6 mm
    outer_wid = cavity_wid + 2 * wall_thk  # 25.1 mm

    # Symmetrical split: 4.5 mm bottom / 4.5 mm top -> 9.0 mm total height
    bottom_height = 4.5
    top_height = 4.5
    total_height = bottom_height + top_height  # 9.0 mm

    under_pcb_clearance = 1.2
    pcb_origin_x = wall_thk + pcb_clearance  # 2.05 mm
    pcb_origin_y = wall_thk + pcb_clearance  # 2.05 mm
    usb_center_x = outer_wid / 2.0           # 12.55 mm

    # -------------------------------------------------------------
    # HELPER: AUTHENTIC TRAPEZOIDAL MICRO-USB CUTTER
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

        w_outer = microusb_wire(11.0, 5.2, 1.3, outer_len + 0.5)
        w_bevel = microusb_wire(8.2, 3.4, 0.85, outer_len - 1.2)
        w_inner = microusb_wire(8.2, 3.4, 0.85, outer_len - wall_thk - 1.5)
        cutter = Part.makeLoft([w_inner, w_bevel, w_outer], True)
        cutter.translate(FreeCAD.Vector(usb_center_x, 0, z_center))
        return cutter

    # -------------------------------------------------------------
    # HELPER: S-CURVE ROUNDED DISHED WELL CUTTER
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
    # 1. BOTTOM HALF ENCLOSURE
    # -------------------------------------------------------------
    outer_box_bottom = Part.makeBox(outer_wid, outer_len, bottom_height)

    # Fillet outer vertical corners
    vert_edges = [
        e for e in outer_box_bottom.Edges if abs(e.Length - bottom_height) < 0.01 and
        (abs(e.Vertexes[0].Point.x) < 0.01 or abs(e.Vertexes[0].Point.x - outer_wid) < 0.01) and
        (abs(e.Vertexes[0].Point.y) < 0.01 or abs(e.Vertexes[0].Point.y - outer_len) < 0.01)
    ]
    if len(vert_edges) == 4:
        outer_box_bottom = outer_box_bottom.makeFillet(corner_rad, vert_edges)

    # Curved fillet on bottom perimeter edges (Z = 0)
    bottom_perimeter_edges = [
        e for e in outer_box_bottom.Edges
        if abs(e.Vertexes[0].Point.z) < 0.01 and abs(e.Vertexes[1].Point.z) < 0.01
    ]
    if bottom_perimeter_edges:
        outer_box_bottom = outer_box_bottom.makeFillet(edge_fillet_rad, bottom_perimeter_edges)

    # Main internal cavity
    inner_cavity = Part.makeBox(cavity_wid, cavity_len, bottom_height - floor_thk + 0.1)
    inner_cavity.translate(FreeCAD.Vector(wall_thk, wall_thk, floor_thk))
    bottom_shell = outer_box_bottom.cut(inner_cavity)

    # -------------------------------------------------------------
    # 4 EXACT-FIT MOUNTING HOLE STANDOFFS & ALIGNMENT PEGS
    # Raspberry Pi Pico mounting holes: (4.8, 2.0) & (4.8, 49.0)
    # -------------------------------------------------------------
    hole_pts = [
        (pcb_origin_x + 4.80, pcb_origin_y + 2.00),
        (pcb_origin_x + 16.20, pcb_origin_y + 2.00),
        (pcb_origin_x + 4.80, pcb_origin_y + 49.00),
        (pcb_origin_x + 16.20, pcb_origin_y + 49.00),
    ]

    peg_r = 0.95        # 1.9 mm dia (fits 2.1mm Pico holes smoothly)
    boss_r_bottom = 1.9  # Standoff support boss under the hole
    standoff_h = under_pcb_clearance # 1.2 mm
    standoff_top_z = floor_thk + standoff_h # 2.6 mm
    peg_protrusion = 1.6 # mm past parting line

    for hx, hy in hole_pts:
        # Cylindrical standoff resting pad under PCB
        standoff = Part.makeCylinder(boss_r_bottom, standoff_h, FreeCAD.Vector(hx, hy, floor_thk), FreeCAD.Vector(0,0,1))
        bottom_shell = bottom_shell.fuse(standoff)

        # Solid alignment friction peg
        total_peg_h = (bottom_height - standoff_top_z) + peg_protrusion # (4.5 - 2.6) + 1.6 = 3.5 mm
        peg_body = Part.makeCylinder(peg_r, total_peg_h - 0.5, FreeCAD.Vector(hx, hy, standoff_top_z), FreeCAD.Vector(0,0,1))
        # 45-degree self-centering lead-in chamfer cone at tip
        peg_tip = Part.makeCone(peg_r, 0.45, 0.5, FreeCAD.Vector(hx, hy, standoff_top_z + total_peg_h - 0.5), FreeCAD.Vector(0,0,1))
        peg = peg_body.fuse(peg_tip)
        bottom_shell = bottom_shell.fuse(peg)

    # Cut lower half of trapezoidal Micro-USB port
    cutter_bottom = make_microusb_cutter(bottom_height)
    bottom_shell = bottom_shell.cut(cutter_bottom)

    # Flank Grip Flutes (5 grooves on left and right)
    flute_depth = 0.45
    flute_w = 1.2
    fl_h_bottom = (bottom_height - edge_fillet_rad) + 0.1
    flutes_bottom = []
    for i in range(5):
        y_pos = 24.0 + i * 2.2
        fl_l = Part.makeBox(flute_depth + 0.1, flute_w, fl_h_bottom)
        fl_l.translate(FreeCAD.Vector(-0.1, y_pos, edge_fillet_rad))
        fl_r = Part.makeBox(flute_depth + 0.1, flute_w, fl_h_bottom)
        fl_r.translate(FreeCAD.Vector(outer_wid - flute_depth, y_pos, edge_fillet_rad))
        flutes_bottom.extend([fl_l, fl_r])
    for f in flutes_bottom:
        bottom_shell = bottom_shell.cut(f)

    # -------------------------------------------------------------
    # 2. TOP HALF ENCLOSURE
    # -------------------------------------------------------------
    outer_box_top = Part.makeBox(outer_wid, outer_len, top_height)

    vert_edges_top = [
        e for e in outer_box_top.Edges if abs(e.Length - top_height) < 0.01 and
        (abs(e.Vertexes[0].Point.x) < 0.01 or abs(e.Vertexes[0].Point.x - outer_wid) < 0.01) and
        (abs(e.Vertexes[0].Point.y) < 0.01 or abs(e.Vertexes[0].Point.y - outer_len) < 0.01)
    ]
    if len(vert_edges_top) == 4:
        outer_box_top = outer_box_top.makeFillet(corner_rad, vert_edges_top)

    top_perimeter_edges = [
        e for e in outer_box_top.Edges
        if abs(e.Vertexes[0].Point.z - top_height) < 0.01 and abs(e.Vertexes[1].Point.z - top_height) < 0.01
    ]
    if top_perimeter_edges:
        outer_box_top = outer_box_top.makeFillet(edge_fillet_rad, top_perimeter_edges)

    # Inner cavity for top shell
    inner_cavity_top = Part.makeBox(cavity_wid, cavity_len, top_height - roof_thk + 0.1)
    inner_cavity_top.translate(FreeCAD.Vector(wall_thk, wall_thk, -0.05))
    top_shell = outer_box_top.cut(inner_cavity_top)

    # Cut upper half of trapezoidal Micro-USB port
    cutter_top = make_microusb_cutter(0.0)
    top_shell = top_shell.cut(cutter_top)

    # Top Deck Recessed Plate (0.35 mm geometric inset)
    inset_w = 17.5
    inset_l = outer_len - 8.5
    inset_d = 0.35
    inset_box = Part.makeBox(inset_w, inset_l, inset_d + 0.1)
    v_inset = [e for e in inset_box.Edges if abs(e.Length - (inset_d + 0.1)) < 0.01]
    if len(v_inset) == 4:
        inset_box = inset_box.makeFillet(2.0, v_inset)
    inset_box.translate(FreeCAD.Vector((outer_wid - inset_w)/2.0, 4.25, top_height - inset_d))
    top_shell = top_shell.cut(inset_box)

    z_floor = top_height - inset_d  # Z = 4.15 mm

    # Dished Wells for BOOTSEL and LED
    boot_x = pcb_origin_x + 7.00
    boot_y = pcb_origin_y + 39.00
    led_x = pcb_origin_x + 4.79
    led_y = pcb_origin_y + 46.19

    boot_well = make_revolved_well(0.9, 2.0, 0.55, 0.35, z_floor)
    boot_well.translate(FreeCAD.Vector(boot_x, boot_y, 0))

    led_well = make_revolved_well(0.7, 1.4, 0.40, 0.30, z_floor)
    led_well.translate(FreeCAD.Vector(led_x, led_y, 0))

    top_shell = top_shell.cut(boot_well).cut(led_well)

    led_halo1 = Part.makeCylinder(2.3, 0.2)
    led_halo2 = Part.makeCylinder(1.9, 0.3)
    led_halo = led_halo1.cut(led_halo2)
    led_halo.translate(FreeCAD.Vector(led_x, led_y, z_floor - 0.15))

    boot_ring1 = Part.makeCylinder(2.9, 0.2)
    boot_ring2 = Part.makeCylinder(2.5, 0.3)
    boot_ring = boot_ring1.cut(boot_ring2)
    boot_ring.translate(FreeCAD.Vector(boot_x, boot_y, z_floor - 0.15))

    top_shell = top_shell.cut(led_halo).cut(boot_ring)

    # -------------------------------------------------------------
    # DEXPAD EXACT CURVED LOGO DEBOSS WITH FLIPPED 3D RECESS
    # User requirement:
    # 1. Exact smooth curve of our logo (not pill-looking boxes).
    # 2. TOP PART IS MORE RECESSED (deeper, 0.55mm) than lower part (0.25mm)!
    # -------------------------------------------------------------
    logo_scale = 10.0 / 60.0

    # A. LOWER PART: The 45-degree capsule (LESS RECESSED = 0.25 mm)
    cap_w = 60.0 * logo_scale  # 10.0 mm
    cap_h = 18.0 * logo_scale  # 3.0 mm
    cap_r = cap_h / 2.0        # 1.5 mm
    lower_depth = 0.25         # SHALLOWER (0.25 mm)

    box_cap = Part.makeBox(cap_w - 2.0*cap_r, cap_h, lower_depth + 0.1)
    box_cap.translate(FreeCAD.Vector(-cap_w/2.0 + cap_r, -cap_r, 0))
    cyl1 = Part.makeCylinder(cap_r, lower_depth + 0.1, FreeCAD.Vector(-cap_w/2.0 + cap_r, 0, 0), FreeCAD.Vector(0,0,1))
    cyl2 = Part.makeCylinder(cap_r, lower_depth + 0.1, FreeCAD.Vector(cap_w/2.0 - cap_r, 0, 0), FreeCAD.Vector(0,0,1))
    lower_part = box_cap.fuse(cyl1).fuse(cyl2)
    lower_part.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 45)
    lower_part.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 180)  # Rotated 180 facing Micro-USB port
    lower_part.translate(FreeCAD.Vector(outer_wid / 2.0, 20.0, z_floor - lower_depth))

    # B. TOP PART: The contoured crossing stroke (MORE RECESSED = 0.55 mm)
    def bezier_pt(p0, p1, p2, p3, t):
        x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        return (x, y)

    pts_svg = []
    for i in range(12):
        t = i / 11.0
        pts_svg.append(bezier_pt((65,21), (69.4,25.4), (69.4,32.6), (65,37), t))
    pts_svg.append((57, 45))
    pts_svg.append((45, 57))
    pts_svg.append((37, 65))
    for i in range(1, 12):
        t = i / 11.0
        pts_svg.append(bezier_pt((37,65), (32.6,69.4), (25.4,69.4), (21,65), t))
    for i in range(1, 12):
        t = i / 11.0
        pts_svg.append(bezier_pt((21,65), (16.6,60.6), (16.6,53.4), (21,49), t))
    pts_svg.append((29, 41))
    pts_svg.append((65, 21))

    pts_fc = []
    for p in pts_svg:
        x = (p[0] - 50.0) * logo_scale
        y = ((p[1] + 3.0) - 50.0) * logo_scale
        pts_fc.append(FreeCAD.Vector(x, y, 0))

    wire_stroke = Part.Wire(Part.makePolygon(pts_fc))
    top_stroke_face = Part.Face(wire_stroke)
    top_depth = 0.55  # DEEPER (0.55 mm) -> Flipped per user instruction!
    top_part = top_stroke_face.extrude(FreeCAD.Vector(0, 0, top_depth + 0.1))
    top_part.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 180)  # Rotated 180 facing Micro-USB port
    top_part.translate(FreeCAD.Vector(outer_wid / 2.0, 20.0, z_floor - top_depth))

    # Cut both from top shell
    top_shell = top_shell.cut(lower_part).cut(top_part)

    # Flank Grip Flutes on top half
    flutes_top = []
    fl_h_top = (top_height - edge_fillet_rad) + 0.1
    for i in range(5):
        y_pos = 24.0 + i * 2.2
        fl_l = Part.makeBox(flute_depth + 0.1, flute_w, fl_h_top)
        fl_l.translate(FreeCAD.Vector(-0.1, y_pos, -0.05))
        fl_r = Part.makeBox(flute_depth + 0.1, flute_w, fl_h_top)
        fl_r.translate(FreeCAD.Vector(outer_wid - flute_depth, y_pos, -0.05))
        flutes_top.extend([fl_l, fl_r])
    for f in flutes_top:
        top_shell = top_shell.cut(f)

    # -------------------------------------------------------------
    # 4 CORNER ALIGNMENT PEG SOCKET BOSSES (ZERO CLIPS / ZERO OUTER HOLES)
    # Positions match hole_pts exactly. Boss stops comfortably above PCB.
    # -------------------------------------------------------------
    sock_r = 1.15  # 2.3 mm dia (fits 1.9mm peg with 0.20 mm radial clearance)
    boss_r_top = 2.2
    boss_top_h = 2.0  # Height of socket boss from ceiling

    for hx, hy in hole_pts:
        boss = Part.makeCylinder(boss_r_top, boss_top_h, FreeCAD.Vector(hx, hy, 0), FreeCAD.Vector(0,0,1))
        hole = Part.makeCylinder(sock_r, boss_top_h + 0.2, FreeCAD.Vector(hx, hy, -0.1), FreeCAD.Vector(0,0,1))
        sock_boss = boss.cut(hole)
        top_shell = top_shell.fuse(sock_boss)

    # -------------------------------------------------------------
    # 3. ADD OBJECTS TO FREECAD DOCUMENT (SIDE-BY-SIDE DISPLAY)
    # -------------------------------------------------------------
    obj_bottom = doc.addObject("Part::Feature", "Pico2W_Bottom_Half")
    obj_bottom.Shape = bottom_shell
    obj_bottom.Label = "Pico 2 W Case - Bottom Half (Friction Pegs)"

    top_display = top_shell.copy()
    top_display.translate(FreeCAD.Vector(outer_wid + 10.0, 0, 0))

    obj_top = doc.addObject("Part::Feature", "Pico2W_Top_Half")
    obj_top.Shape = top_display
    obj_top.Label = "Pico 2 W Case - Top Half (Flipped Stepped Logo & Sockets)"

    try:
        obj_bottom.ViewObject.ShapeColor = (0.55, 0.75, 0.95)
        obj_top.ViewObject.ShapeColor = (0.55, 0.75, 0.95)
    except Exception:
        pass

    doc.recompute()
    print("Enclosure updated successfully!")
    print(f"Dimensions: {outer_wid:.1f} mm (W) x {outer_len:.1f} mm (L) x {total_height:.1f} mm (H)")

    # -------------------------------------------------------------
    # 4. EXPORT STEP / STL / FCStd FILES
    # -------------------------------------------------------------
    if export_files:
        os.makedirs(output_dir, exist_ok=True)
        fcstd_path = os.path.join(output_dir, "pico2w_enclosure.FCStd")
        doc.saveAs(os.path.abspath(fcstd_path))

        step_bottom = os.path.join(output_dir, "pico2w_case_bottom.step")
        step_top = os.path.join(output_dir, "pico2w_case_top.step")
        bottom_shell.exportStep(os.path.abspath(step_bottom))
        top_shell.exportStep(os.path.abspath(step_top))

        stl_bottom = os.path.join(output_dir, "pico2w_case_bottom.stl")
        stl_top = os.path.join(output_dir, "pico2w_case_top.stl")

        mesh_bottom = Mesh.Mesh()
        mesh_bottom.addFacets(bottom_shell.tessellate(0.05))
        mesh_bottom.write(os.path.abspath(stl_bottom))

        mesh_top = Mesh.Mesh()
        mesh_top.addFacets(top_shell.tessellate(0.05))
        mesh_top.write(os.path.abspath(stl_top))

    return doc

if __name__ == "__main__":
    create_enclosure()
