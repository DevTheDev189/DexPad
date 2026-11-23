import os
import FreeCAD
import Part
import Draft

doc = FreeCAD.activeDocument()
print("Active doc:", doc.Name if doc else None)

font = "C:/Windows/Fonts/arialbd.ttf"
if not os.path.exists(font):
    font = "C:/Windows/Fonts/arial.ttf"
print("Font exists:", os.path.exists(font))

# Test ShapeString
ss = Draft.make_shapestring(String="DEXTER", FontFile=font, Size=3.2)
doc.recompute()
print("ShapeString created:", ss.Name, "wires:", len(ss.Shape.Wires))
# Remove test shapestring
doc.removeObject(ss.Name)
doc.recompute()
print("Cleaned up test shapestring.")
