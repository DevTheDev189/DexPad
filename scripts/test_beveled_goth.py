import os
import math
import FreeCAD
import Part
import Draft

doc = FreeCAD.newDocument("test_beveled")

# 1. Test Times New Roman font
font_file = "C:/Windows/Fonts/timesbd.ttf"
if not os.path.exists(font_file):
    font_file = "C:/Windows/Fonts/times.ttf"

ss = Draft.make_shapestring(String="DEXTER", FontFile=font_file, Size=2.8)
doc.recompute()
bb = ss.Shape.BoundBox
print("Times font loaded successfully! Width:", bb.XMax - bb.XMin, "Height:", bb.YMax - bb.YMin)

# 2. Test Tilted, Bigger Broken Heart
def make_broken_heart(cx, cy, size, h, tilt_deg, z_base):
    s2 = size / 2.0
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
    heart = s_l.fuse(s_r)
    # Tilt
    heart.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), tilt_deg)
    heart.translate(FreeCAD.Vector(cx, cy, z_base))
    return heart

heart = make_broken_heart(-5.8, 10.0, 7.2, 0.45, -15.0, 0)
print("Heart volume:", heart.Volume)

# 3. Test Bigger X-Patch
def make_x_patch(cx, cy, size, bar_w, h, z_base):
    b1 = Part.makeBox(size, bar_w, h)
    b1.translate(FreeCAD.Vector(-size/2.0, -bar_w/2.0, 0))
    ve1 = [e for e in b1.Edges if abs(e.Length - h) < 0.01 and (abs(e.Vertexes[0].Point.x - size/2.0) < 0.01 or abs(e.Vertexes[0].Point.x + size/2.0) < 0.01)]
    if len(ve1) == 4:
        b1 = b1.makeFillet(bar_w * 0.45, ve1)
    b1.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 45)
    
    b2 = Part.makeBox(size, bar_w, h)
    b2.translate(FreeCAD.Vector(-size/2.0, -bar_w/2.0, 0))
    ve2 = [e for e in b2.Edges if abs(e.Length - h) < 0.01 and (abs(e.Vertexes[0].Point.x - size/2.0) < 0.01 or abs(e.Vertexes[0].Point.x + size/2.0) < 0.01)]
    if len(ve2) == 4:
        b2 = b2.makeFillet(bar_w * 0.45, ve2)
    b2.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), -45)
    
    x_solid = b1.fuse(b2)
    x_solid.translate(FreeCAD.Vector(cx, cy, z_base))
    return x_solid

x_patch = make_x_patch(6.2, 11.0, 8.5, 2.2, 0.45, 0)
print("X patch volume:", x_patch.Volume)

# 4. Test Bigger Frankenstein Stitches
def make_raised_stitches(x1, y1, x2, y2, n_stitches, stitch_len, line_w, h, z_base):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx**2 + dy**2)
    angle = math.degrees(math.atan2(dy, dx))
    
    seam = Part.makeBox(dist, line_w, h * 0.8)
    seam.translate(FreeCAD.Vector(0, -line_w/2.0, 0))
    seam.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), angle)
    seam.translate(FreeCAD.Vector(x1, y1, z_base))
    
    solids = [seam]
    sl2 = stitch_len / 2.0
    for i in range(1, n_stitches + 1):
        t = i / float(n_stitches + 1)
        cx = x1 + dx * t
        cy = y1 + dy * t
        st = Part.makeBox(line_w * 1.3, stitch_len, h)
        st.translate(FreeCAD.Vector(-line_w * 0.65, -sl2, 0))
        ves = [e for e in st.Edges if abs(e.Length - h) < 0.01 and (abs(e.Vertexes[0].Point.y - sl2) < 0.01 or abs(e.Vertexes[0].Point.y + sl2) < 0.01)]
        if len(ves) == 4:
            try:
                st = st.makeFillet(line_w * 0.5, ves)
            except Exception:
                pass
        st.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), angle)
        st.translate(FreeCAD.Vector(cx, cy, z_base))
        solids.append(st)
        
    res = solids[0]
    for s in solids[1:]:
        res = res.fuse(s)
    return res

stitches = make_raised_stitches(-3.0, 15.0, -10.0, 20.5, 4, 3.8, 0.85, 0.45, 0)
print("Stitches volume:", stitches.Volume)

FreeCAD.closeDocument("test_beveled")
