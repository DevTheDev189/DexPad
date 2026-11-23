import os
import math
import FreeCAD
import Part
import Draft

doc = FreeCAD.newDocument("test_fixes")

# -------------------------------------------------------------
# 1. TEST BEVELED TEXT
# -------------------------------------------------------------
font_file = "C:/Windows/Fonts/timesbd.ttf"
ss = Draft.make_shapestring(String="DEXTER", FontFile=font_file, Size=2.4)
doc.recompute()
text_shape = ss.Shape

# Test A: Bevel text by lofting from wire to wire, or chamfering
# Let's see what wires are in text_shape
print("Text wires:", len(text_shape.Wires))
# Can we chamfer or fillet text_solid?
text_solid = text_shape.extrude(FreeCAD.Vector(0, 0, 0.40))
top_e = [e for e in text_solid.Edges if abs(e.Vertexes[0].Point.z - 0.40) < 0.01 and abs(e.Vertexes[1].Point.z - 0.40) < 0.01]
print("Text top edges:", len(top_e))
try:
    text_fillet = text_solid.makeFillet(0.04, top_e)
    print("Direct text fillet succeeded!")
except Exception as e:
    print("Direct text fillet failed:", e)

# Test B: Inset loft or 2.5D draft bevel
# Let's test making a raised beveled cartouche badge with beveled letters
# Or lofting each character wire to an offset wire
try:
    lofted_solids = []
    for w in text_shape.Wires:
        # Check wire orientation
        pass
except Exception as e:
    pass

# -------------------------------------------------------------
# 2. TEST BEVELED CURVED STITCH SEAM LINE
# -------------------------------------------------------------
# A rounded cord / half-cylinder swept along the curved bezier spine!
p0 = (1.0, 4.5)
p_ctrl = (5.5, 11.5)
p1 = (11.5, 19.5)

def bezier_pt(t):
    x = (1-t)**2 * p0[0] + 2*(1-t)*t * p_ctrl[0] + t**2 * p1[0]
    y = (1-t)**2 * p0[1] + 2*(1-t)*t * p_ctrl[1] + t**2 * p1[1]
    return x, y

# Sweep a semicircle or arched profile along the bezier wire
# Or make overlapping spherical/cylindrical beads along the curve!
# If we place overlapping cylinders or spheres along the curve, it forms a perfectly round/beveled bead cord!
n_beads = 40
beads = []
r_cord = 0.45
h_cord = 0.35
for i in range(n_beads + 1):
    t = i / float(n_beads)
    cx, cy = bezier_pt(t)
    # Semicircular dome / sphere or cylinder
    cyl = Part.makeCylinder(r_cord, h_cord)
    # Fillet top edge of cylinder
    te = [e for e in cyl.Edges if abs(e.Vertexes[0].Point.z - h_cord) < 0.01]
    try:
        cyl = cyl.makeFillet(r_cord * 0.7, te)
    except Exception:
        pass
    cyl.translate(FreeCAD.Vector(cx, cy, 0))
    beads.append(cyl)

seam_cord = beads[0]
for b in beads[1:]:
    seam_cord = seam_cord.fuse(b)

print("Beveled seam cord created! Volume:", seam_cord.Volume)

# -------------------------------------------------------------
# 3. TEST PROTRUDING & BEVELED BOTTOM FEATURES
# -------------------------------------------------------------
# On bottom shell, bottom surface is at Z = 0.
# If features protrude in -Z direction:
# Base at Z = 0, extends to Z = -0.45 mm!
# And the top (which is facing downwards at Z = -0.45) MUST have its perimeter edges filleted!

FreeCAD.closeDocument("test_fixes")
