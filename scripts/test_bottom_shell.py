import FreeCAD
import Part
import math

doc = FreeCAD.newDocument("test_bottom")

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

# 3. Build Bottom Shell
h_bottom = 4.3
face_bottom = make_coffin_polygon()
solid_bottom = face_bottom.extrude(FreeCAD.Vector(0, 0, h_bottom))

# Vertical fillets
vert_edges = [e for e in solid_bottom.Edges if abs(e.Length - h_bottom) < 0.01]
solid_bottom = solid_bottom.makeFillet(1.4, vert_edges)

# Bottom perimeter fillet (Z=0)
bot_edges = [e for e in solid_bottom.Edges if abs(e.Vertexes[0].Point.z) < 0.01 and abs(e.Vertexes[1].Point.z) < 0.01]
solid_bottom = solid_bottom.makeFillet(1.0, bot_edges)

# Internal rectangular cavity
cavity_w = 21.7
cavity_l = 51.7
cavity_y_start = 1.8
floor_thk = 1.5

inner_cavity = Part.makeBox(cavity_w, cavity_l, h_bottom - floor_thk + 0.1)
inner_cavity.translate(FreeCAD.Vector(-cavity_w/2.0, cavity_y_start, floor_thk))
bottom_shell = solid_bottom.cut(inner_cavity)

# 4 Corner PCB rest ledges (3.2 x 3.2 x 1.2 mm)
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

# Snap-fit female catch slots (X = +- 10.85, Y = 13.8, 41.5)
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

# Cut Micro-USB port
usb_cutter = make_microusb_cutter(h_bottom)
bottom_shell = bottom_shell.cut(usb_cutter)

print("Bottom shell complete! Volume:", bottom_shell.Volume, "Solids:", len(bottom_shell.Solids))

obj = doc.addObject("Part::Feature", "BottomShell")
obj.Shape = bottom_shell
doc.recompute()
FreeCAD.closeDocument("test_bottom")
