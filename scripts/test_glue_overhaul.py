import sys
import os
import math

scripts_dir = r"c:\Users\dwinslow\Documents\Dexter_Controller_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import FreeCAD
import Part

doc = FreeCAD.newDocument("test_glue_overhaul")

# Parametric dimensions
pcb_len = 51.0
pcb_wid = 21.0
pcb_thk = 1.0
pcb_clearance = 0.35

cavity_len = pcb_len + 2 * pcb_clearance  # 51.7 mm
cavity_wid = pcb_wid + 2 * pcb_clearance  # 21.7 mm

cavity_y_start = 1.8
total_len = 56.0

bottom_height = 4.3
top_height = 4.3
floor_thk = 1.5
roof_thk = 1.5
under_pcb_clearance = 1.2

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

# Solid base
solid_bottom = Part.Face(wire_coffin).extrude(FreeCAD.Vector(0, 0, bottom_height))
vert_edges = [e for e in solid_bottom.Edges if abs(e.Length - bottom_height) < 0.01]
solid_bottom = solid_bottom.makeFillet(1.4, vert_edges)

inner_cavity = Part.makeBox(cavity_wid, cavity_len, bottom_height - floor_thk + 0.1)
inner_cavity.translate(FreeCAD.Vector(-cavity_wid/2.0, cavity_y_start, floor_thk))
bottom_shell = solid_bottom.cut(inner_cavity)

# PCB corner rest ledges
ledge_x = 5.8
ledge_y = 4.0
ledge_h = under_pcb_clearance
ledges = [
    Part.makeBox(ledge_x, ledge_y, ledge_h),
    Part.makeBox(ledge_x, ledge_y, ledge_h),
    Part.makeBox(ledge_x, ledge_y, ledge_h),
    Part.makeBox(ledge_x, ledge_y, ledge_h)
]
ledges[0].translate(FreeCAD.Vector(-cavity_wid/2.0, cavity_y_start, floor_thk))
ledges[1].translate(FreeCAD.Vector(cavity_wid/2.0 - ledge_x, cavity_y_start, floor_thk))
ledges[2].translate(FreeCAD.Vector(-cavity_wid/2.0, cavity_y_start + cavity_len - ledge_y, floor_thk))
ledges[3].translate(FreeCAD.Vector(cavity_wid/2.0 - ledge_x, cavity_y_start + cavity_len - ledge_y, floor_thk))
for l in ledges:
    bottom_shell = bottom_shell.fuse(l)

# 4 PCB Locating Nubs into Pico 2 W M2 mounting holes
nub_r = 0.90 # 1.8mm diameter (into 2.1mm Pico hole)
nub_h = 0.85
nubs = [
    Part.makeCylinder(nub_r, nub_h),
    Part.makeCylinder(nub_r, nub_h),
    Part.makeCylinder(nub_r, nub_h),
    Part.makeCylinder(nub_r, nub_h)
]
z_nub = floor_thk + ledge_h
nubs[0].translate(FreeCAD.Vector(-5.7, cavity_y_start + 2.0, z_nub))
nubs[1].translate(FreeCAD.Vector(5.7, cavity_y_start + 2.0, z_nub))
nubs[2].translate(FreeCAD.Vector(-5.7, cavity_y_start + 49.0, z_nub))
nubs[3].translate(FreeCAD.Vector(5.7, cavity_y_start + 49.0, z_nub))
for n in nubs:
    bottom_shell = bottom_shell.fuse(n)

# Robust Alignment Pins in Bat Wings on parting line (Z = bottom_height)
pin_r = 1.15 # 2.3mm diameter
pin_h = 1.8
pin_l = Part.makeCylinder(pin_r, pin_h).fuse(Part.makeCone(pin_r, 0.6, 0.4).translate(FreeCAD.Vector(0,0,pin_h)))
pin_r_wing = Part.makeCylinder(pin_r, pin_h).fuse(Part.makeCone(pin_r, 0.6, 0.4).translate(FreeCAD.Vector(0,0,pin_h)))

pin_l.translate(FreeCAD.Vector(-13.8, 41.5, bottom_height))
pin_r_wing.translate(FreeCAD.Vector(13.8, 41.5, bottom_height))
bottom_shell = bottom_shell.fuse(pin_l).fuse(pin_r_wing)

# 3-Sided Stepped Interlocking Tongue on Bottom Shell (left, right, head)
tongue_h = 0.90
tongue_thk = 0.70
tongue_clr = 0.18 # SLA clearance

# Left tongue
t_left = Part.makeBox(tongue_thk, cavity_len - 3.5, tongue_h)
t_left.translate(FreeCAD.Vector(-cavity_wid/2.0 + tongue_clr, cavity_y_start + 3.5, bottom_height))

# Right tongue
t_right = Part.makeBox(tongue_thk, cavity_len - 3.5, tongue_h)
t_right.translate(FreeCAD.Vector(cavity_wid/2.0 - tongue_clr - tongue_thk, cavity_y_start + 3.5, bottom_height))

# Head tongue
t_head = Part.makeBox(cavity_wid - 2.0, tongue_thk, tongue_h)
t_head.translate(FreeCAD.Vector(-cavity_wid/2.0 + 1.0, cavity_y_start + cavity_len - tongue_clr - tongue_thk, bottom_height))

bottom_shell = bottom_shell.fuse(t_left).fuse(t_right).fuse(t_head)

print("Bottom shell with pins, nubs, and tongue successfully generated!")
print(f"Solids: {len(bottom_shell.Solids)}, Volume: {bottom_shell.Volume:.2f}")

# Top shell
solid_top = Part.Face(wire_coffin).extrude(FreeCAD.Vector(0, 0, top_height))
vert_edges_top = [e for e in solid_top.Edges if abs(e.Length - top_height) < 0.01]
solid_top = solid_top.makeFillet(1.4, vert_edges_top)

inner_cavity_top = Part.makeBox(cavity_wid, cavity_len, top_height - roof_thk + 0.1)
inner_cavity_top.translate(FreeCAD.Vector(-cavity_wid/2.0, cavity_y_start, -0.05))
top_shell = solid_top.cut(inner_cavity_top)

# Sockets in top shell for bat wing pins (at Z = 0)
socket_r = 1.35 # 2.7mm diameter (0.20mm radial clearance)
socket_h = 2.4
sock_l = Part.makeCylinder(socket_r, socket_h)
sock_r = Part.makeCylinder(socket_r, socket_h)
sock_l.translate(FreeCAD.Vector(-13.8, 41.5, -0.01))
sock_r.translate(FreeCAD.Vector(13.8, 41.5, -0.01))

top_shell = top_shell.cut(sock_l).cut(sock_r)

print("Top shell with sockets successfully generated!")
print(f"Solids: {len(top_shell.Solids)}, Volume: {top_shell.Volume:.2f}")

FreeCAD.closeDocument("test_glue_overhaul")
