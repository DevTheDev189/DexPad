import FreeCAD
import Part

doc = FreeCAD.newDocument("test_heart_bevel")

def make_beveled_heart():
    size = 7.2
    s2 = size / 2.0
    h = 0.45
    pts_left = [
        FreeCAD.Vector(-0.15, s2 * 0.40, 0),
        FreeCAD.Vector(-s2 * 0.50, s2 * 0.95, 0),
        FreeCAD.Vector(-s2 * 0.95, s2 * 0.45, 0),
        FreeCAD.Vector(-s2 * 0.70, -s2 * 0.20, 0),
        FreeCAD.Vector(-0.15, -s2 * 0.90, 0),
        FreeCAD.Vector(-0.40, -s2 * 0.40, 0),
        FreeCAD.Vector(-0.10, -s2 * 0.05, 0),
        FreeCAD.Vector(-0.35, s2 * 0.20, 0),
        FreeCAD.Vector(-0.15, s2 * 0.40, 0)
    ]
    s_l = Part.Face(Part.Wire(Part.makePolygon(pts_left))).extrude(FreeCAD.Vector(0, 0, h))
    
    pts_right = [
        FreeCAD.Vector(0.15, s2 * 0.40 + 0.15, 0),
        FreeCAD.Vector(0.35, s2 * 0.20 + 0.15, 0),
        FreeCAD.Vector(0.10, -s2 * 0.05 + 0.15, 0),
        FreeCAD.Vector(0.40, -s2 * 0.40 + 0.15, 0),
        FreeCAD.Vector(0.15, -s2 * 0.90 + 0.15, 0),
        FreeCAD.Vector(s2 * 0.70, -s2 * 0.20 + 0.15, 0),
        FreeCAD.Vector(s2 * 0.95, s2 * 0.45 + 0.15, 0),
        FreeCAD.Vector(s2 * 0.50, s2 * 0.95 + 0.15, 0),
        FreeCAD.Vector(0.15, s2 * 0.40 + 0.15, 0)
    ]
    s_r = Part.Face(Part.Wire(Part.makePolygon(pts_right))).extrude(FreeCAD.Vector(0, 0, h))
    
    # Try fillet on top edges
    top_l = [e for e in s_l.Edges if abs(e.Vertexes[0].Point.z - h) < 0.01 and abs(e.Vertexes[1].Point.z - h) < 0.01]
    top_r = [e for e in s_r.Edges if abs(e.Vertexes[0].Point.z - h) < 0.01 and abs(e.Vertexes[1].Point.z - h) < 0.01]
    try:
        s_l = s_l.makeFillet(0.12, top_l)
        s_r = s_r.makeFillet(0.12, top_r)
        print("Heart fillet succeeded!")
    except Exception as e:
        print("Heart fillet error:", e)
        
    heart = s_l.fuse(s_r)
    return heart

h = make_beveled_heart()
print("Heart volume:", h.Volume)
FreeCAD.closeDocument("test_heart_bevel")
