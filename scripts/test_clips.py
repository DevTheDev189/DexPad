import os
import math
import FreeCAD
import Part

doc = FreeCAD.newDocument("test_clips")

# Let's import the previous top shell logic and fuse cantilever tabs
h_top = 4.3
cavity_w = 21.7
cavity_l = 51.7
cavity_y_start = 1.8
roof_thk = 1.5
z_ceil = h_top - roof_thk  # 2.8 mm

snap_tol = 0.20
tab_w = 4.0
tab_thk = 1.0
hook_proj = 0.45
z_root = 3.5
z_catch = -0.7
z_barb = -1.2
z_tip = -2.4
snap_y1 = cavity_y_start + 12.0
snap_y2 = cavity_y_start + cavity_l - 12.0

# Left clip profile (in XZ plane, at X = -cavity_w/2.0 = -10.85)
# Wall is at X <= -10.85. The clip body is inside the cavity at X in [-10.85 + snap_tol, -10.85 + snap_tol + tab_thk]
# Hook projects back towards wall into the catch slot (X < -10.85 + snap_tol)
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

# Right clip profile (at X = +cavity_w/2.0 = +10.85)
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

all_tabs = t_l1.fuse(t_l2).fuse(t_r1).fuse(t_r2)
print("Tabs created successfully! Volume:", all_tabs.Volume)

FreeCAD.closeDocument("test_clips")
