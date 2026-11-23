import FreeCAD
import Part
import math

doc = FreeCAD.newDocument("test_bevel_tech")

# Test 1: Slime drape bevel
# Can we make a 3D solid and fillet the top perimeter edge?
# Let's test makeFillet on a curved polygon solid:
pts = [
    FreeCAD.Vector(-10, 20, 0),
    FreeCAD.Vector(10, 20, 0),
    FreeCAD.Vector(10, 10, 0),
    FreeCAD.Vector(5, 5, 0),
    FreeCAD.Vector(0, 8, 0),
    FreeCAD.Vector(-5, 4, 0),
    FreeCAD.Vector(-10, 10, 0),
    FreeCAD.Vector(-10, 20, 0)
]
w = Part.Wire(Part.makePolygon(pts))
f = Part.Face(w)
s = f.extrude(FreeCAD.Vector(0, 0, 0.45))

# Top edges are those with z == 0.45
top_e = [e for e in s.Edges if abs(e.Vertexes[0].Point.z - 0.45) < 0.01 and abs(e.Vertexes[1].Point.z - 0.45) < 0.01]
print("Top edges count:", len(top_e))
try:
    s_filleted = s.makeFillet(0.15, top_e)
    print("Fillet succeeded! Faces:", len(s_filleted.Faces))
except Exception as e:
    print("Fillet failed:", e)

# Test 2: Draft / Chamfer or 2D Offset loft
try:
    # 2D wire offset in Draft or Part
    w_inset = w.makeOffset2D(-0.25)
    f_bot = Part.Face(w)
    f_top = Part.Face(w_inset)
    f_top.translate(FreeCAD.Vector(0, 0, 0.45))
    s_lofted = Part.makeLoft([w, w_inset], True) # solid loft
    print("2D Offset Loft succeeded! Volume:", s_lofted.Volume)
except Exception as e:
    print("2D Offset Loft failed:", e)

FreeCAD.closeDocument("test_bevel_tech")
