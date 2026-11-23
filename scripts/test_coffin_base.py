import FreeCAD
import Part
import math

doc = FreeCAD.newDocument("test_coffin")

pts_right = [
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Vector(12.7, 0, 0),         # Foot corner
    FreeCAD.Vector(14.5, 37.0, 0),      # Pre-shoulder
    FreeCAD.Vector(16.5, 42.0, 0),      # Wingtip flare
    FreeCAD.Vector(15.2, 44.5, 0),      # Wing scallop notch
    FreeCAD.Vector(14.2, 47.0, 0),      # Upper shoulder
    FreeCAD.Vector(12.8, 56.0, 0),      # Head corner
    FreeCAD.Vector(0, 56.0, 0),         # Head center
]
pts_left = [FreeCAD.Vector(-p.x, p.y, 0) for p in reversed(pts_right[1:-1])]
all_pts = pts_right + pts_left + [pts_right[0]]
wire = Part.Wire(Part.makePolygon(all_pts))
face = Part.Face(wire)
solid = face.extrude(FreeCAD.Vector(0, 0, 4.3))

vert_edges = [e for e in solid.Edges if abs(e.Length - 4.3) < 0.01]
solid = solid.makeFillet(1.5, vert_edges)

# Fillet bottom perimeter edges (Z=0)
bot_edges = [e for e in solid.Edges if abs(e.Vertexes[0].Point.z) < 0.01 and abs(e.Vertexes[1].Point.z) < 0.01]
print("Found bot edges:", len(bot_edges))
try:
    solid = solid.makeFillet(1.0, bot_edges)
    print("Bot perimeter fillet succeeded! Volume:", solid.Volume)
except Exception as e:
    print("Bot perimeter fillet failed:", e)

# Cut inner cavity
inner_cavity = Part.makeBox(21.7, 51.7, 4.3 - 1.5 + 0.1)
inner_cavity.translate(FreeCAD.Vector(-21.7/2.0, 1.8, 1.5))
shell = solid.cut(inner_cavity)
print("Inner cavity cut succeeded! Volume:", shell.Volume, "Solids:", len(shell.Solids))

obj = doc.addObject("Part::Feature", "TestSolid")
obj.Shape = shell
doc.recompute()
FreeCAD.closeDocument("test_coffin")
