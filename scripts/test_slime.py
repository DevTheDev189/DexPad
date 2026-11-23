import FreeCAD
import Part
import math

doc = FreeCAD.newDocument("test_slime")

def make_organic_slime(z_base, h_drip):
    # Construct smooth curved drip profile
    # Define control points with smooth arc sampling
    pts = [
        FreeCAD.Vector(-12.5, 56.0, 0),
        FreeCAD.Vector(12.5, 56.0, 0),
        FreeCAD.Vector(13.8, 49.0, 0),
        FreeCAD.Vector(15.2, 45.0, 0),
    ]
    
    # Helper to append an arc (lobe or valley)
    def append_arc(cx, cy, r, a_start, a_end, n_steps=6):
        for i in range(n_steps + 1):
            t = i / float(n_steps)
            ang = math.radians(a_start + (a_end - a_start) * t)
            pts.append(FreeCAD.Vector(cx + r * math.cos(ang), cy + r * math.sin(ang), 0))

    # Drip 1 (Far right shoulder, reaches Y=40.0, r=1.4)
    # Approach from (15.2, 45.0) down to (14.2, 41.4)
    pts.append(FreeCAD.Vector(14.8, 42.5, 0))
    append_arc(13.2, 40.8, 1.4, 0, -180, 6) # arc bottom
    # Valley 1 (between drip 1 and drip 2, r=1.6 concave)
    append_arc(10.2, 43.5, 1.6, 0, 180, 5)  # valley notch
    # Drip 2 (Mid right, reaches Y=40.5, r=1.5)
    append_arc(7.2, 41.5, 1.5, 0, -180, 6)
    # Valley 2 (concave)
    append_arc(4.2, 44.5, 1.5, 0, 180, 5)
    # Drip 3 (Center long drip! reaches Y=36.0, r=1.8 bulbous droplet!)
    # Necking in slightly before the bulbous drop:
    pts.append(FreeCAD.Vector(1.3, 39.5, 0))
    pts.append(FreeCAD.Vector(1.8, 38.0, 0))
    append_arc(0.0, 37.0, 1.8, 20, -200, 8)
    pts.append(FreeCAD.Vector(-1.8, 38.0, 0))
    pts.append(FreeCAD.Vector(-1.3, 39.5, 0))
    # Valley 3 (concave)
    append_arc(-3.8, 44.0, 1.5, 0, 180, 5)
    # Drip 4 (Mid left, reaches Y=39.5, r=1.5)
    append_arc(-6.8, 41.0, 1.5, 0, -180, 6)
    # Valley 4 (concave)
    append_arc(-9.8, 43.8, 1.5, 0, 180, 5)
    # Drip 5 (Far left shoulder, reaches Y=40.5, r=1.4)
    append_arc(-12.6, 41.2, 1.4, 0, -180, 6)
    
    pts.append(FreeCAD.Vector(-14.8, 42.5, 0))
    pts.append(FreeCAD.Vector(-15.2, 45.0, 0))
    pts.append(FreeCAD.Vector(-13.8, 49.0, 0))
    pts.append(FreeCAD.Vector(-12.5, 56.0, 0))
    
    wire = Part.Wire(Part.makePolygon(pts))
    face = Part.Face(wire)
    solid = face.extrude(FreeCAD.Vector(0, 0, h_drip))
    solid.translate(FreeCAD.Vector(0, 0, z_base))
    
    # Detached falling droplet 1 (below center drip at X=0, Y=33.5)
    drop1 = Part.makeCylinder(1.2, h_drip)
    drop1.translate(FreeCAD.Vector(0, 33.5, z_base))
    
    # Detached falling droplet 2 (below right drip at X=7.2, Y=37.5)
    drop2 = Part.makeCylinder(0.9, h_drip)
    drop2.translate(FreeCAD.Vector(7.2, 37.5, z_base))
    
    return solid.fuse(drop1).fuse(drop2)

slime = make_organic_slime(0, 0.45)
obj = doc.addObject("Part::Feature", "Slime")
obj.Shape = slime
doc.recompute()
print("Organic slime solid created! Volume:", slime.Volume)
FreeCAD.closeDocument("test_slime")
