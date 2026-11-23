import FreeCAD, Part, Draft

doc = FreeCAD.activeDocument()
font = "C:/Windows/Fonts/arialbd.ttf"
ss = Draft.make_shapestring(String="DEXTER", FontFile=font, Size=3.0)
doc.recompute()

# Center the text:
bb = ss.Shape.BoundBox
text_w = bb.XMax - bb.XMin
text_h = bb.YMax - bb.YMin
print("Text dimensions: W=", text_w, "H=", text_h)

# Extrude text
depth = 0.25
text_solid = ss.Shape.extrude(FreeCAD.Vector(0, 0, -(depth + 0.1)))
print("Text solid volume:", text_solid.Volume, "Valid:", text_solid.isValid())

# Test cutting into a box
box = Part.makeBox(20, 20, 4.3)
# Center text in box at (10, 10, 4.3)
text_solid.translate(FreeCAD.Vector(10.0 - text_w/2.0 - bb.XMin, 10.0 - text_h/2.0 - bb.YMin, 4.3))
cut_box = box.cut(text_solid)
print("Cut box volume:", cut_box.Volume, "Valid:", cut_box.isValid())

doc.removeObject(ss.Name)
doc.recompute()
