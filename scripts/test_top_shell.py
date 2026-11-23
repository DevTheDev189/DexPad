import os
import math
import FreeCAD
import Part
import Draft

doc = FreeCAD.newDocument("test_top")

# 1. Base Coffin Polygon with Integrated Bat Wings
def make_coffin_polygon():
    pts_right = [
        FreeCAD.Vector(0, 0, 0),
        FreeCAD.Vector(12.7, 0, 0),         # Foot corner
        FreeCAD.Vector(14.5, 36.0, 0),      # Lower flank
        FreeCAD.Vector(16.5, 41.5, 0),      # Primary wingtip flare
        FreeCAD.Vector(15.0, 44.0, 0),      # Wing scallop notch
        FreeCAD.Vector(15.6, 46.5, 0),      # Secondary wingtip
        FreeCAD.Vector(14.0, 49.0, 0),      # Upper shoulder
        FreeCAD.Vector(12.7, 56.0, 0),      # Head corner
        FreeCAD.Vector(0, 56.0, 0),         # Head center
    ]
    pts_left = [FreeCAD.Vector(-p.x, p.y, 0) for p in reversed(pts_right[1:-1])]
    all_pts = pts_right + pts_left + [pts_right[0]]
    wire = Part.Wire(Part.makePolygon(all_pts))
    face = Part.Face(wire)
    return face

# 2. Authentic Micro-USB Cutter
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

# 3. Camera-Style Concave Well Cutter
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

h_top = 4.3
face_top = make_coffin_polygon()
solid_top = face_top.extrude(FreeCAD.Vector(0, 0, h_top))

# Fillet vertical edges
vert_edges = [e for e in solid_top.Edges if abs(e.Length - h_top) < 0.01]
solid_top = solid_top.makeFillet(1.4, vert_edges)

# Fillet top perimeter (Z = 4.3)
top_edges = [e for e in solid_top.Edges if abs(e.Vertexes[0].Point.z - h_top) < 0.01 and abs(e.Vertexes[1].Point.z - h_top) < 0.01]
solid_top = solid_top.makeFillet(1.0, top_edges)

# Internal rectangular cavity
cavity_w = 21.7
cavity_l = 51.7
cavity_y_start = 1.8
roof_thk = 1.5

inner_cavity = Part.makeBox(cavity_w, cavity_l, h_top - roof_thk + 0.1)
inner_cavity.translate(FreeCAD.Vector(-cavity_w/2.0, cavity_y_start, -0.05))
top_shell = solid_top.cut(inner_cavity)

# Cut Micro-USB port (Z = 0)
usb_cutter = make_microusb_cutter(0.0)
top_shell = top_shell.cut(usb_cutter)

# Cut BOOTSEL and LED wells
boot_x = -3.50
boot_y = cavity_y_start + 39.00  # 40.80 mm
led_x = -5.71
led_y = cavity_y_start + 46.19   # 47.99 mm

boot_well = make_revolved_well(0.9, 2.0, 0.55, 0.35, h_top)
boot_well.translate(FreeCAD.Vector(boot_x, boot_y, 0))

led_well = make_revolved_well(0.7, 1.4, 0.40, 0.30, h_top)
led_well.translate(FreeCAD.Vector(led_x, led_y, 0))

top_shell = top_shell.cut(boot_well).cut(led_well)

# Concentric accent rings
led_ring = Part.makeCylinder(2.3, 0.2).cut(Part.makeCylinder(1.8, 0.3))
led_ring.translate(FreeCAD.Vector(led_x, led_y, h_top - 0.15))

boot_ring = Part.makeCylinder(2.8, 0.2).cut(Part.makeCylinder(2.4, 0.3))
boot_ring.translate(FreeCAD.Vector(boot_x, boot_y, h_top - 0.15))

top_shell = top_shell.cut(led_ring).cut(boot_ring)

print("Top shell base complete! Volume:", top_shell.Volume, "Solids:", len(top_shell.Solids))

obj = doc.addObject("Part::Feature", "TopShell")
obj.Shape = top_shell
doc.recompute()
FreeCAD.closeDocument("test_top")
