import FreeCAD
import Part

doc = FreeCAD.newDocument("test_pill")

# Test 1: Box with rounded vertical corners and top edge fillet
b = Part.makeBox(6.0, 1.8, 0.6)
b.translate(FreeCAD.Vector(-3.0, -0.9, 0))
# Fillet vertical edges
vert_e = [e for e in b.Edges if abs(e.Length - 0.6) < 0.01]
b = b.makeFillet(0.85, vert_e)
# Fillet top edge
top_e = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - 0.6) < 0.01 and abs(e.Vertexes[1].Point.z - 0.6) < 0.01]
try:
    b = b.makeFillet(0.2, top_e)
    print("Pill filleted successfully! Faces:", len(b.Faces))
except Exception as e:
    print("Top fillet failed:", e)

obj = doc.addObject("Part::Feature", "Pill")
obj.Shape = b
doc.recompute()
FreeCAD.closeDocument("test_pill")
