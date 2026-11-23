import FreeCAD
import Part
import math

doc = FreeCAD.newDocument("test_features")

# 1. Test Drip Polygon
def make_drip_solid(z_base, h_drip):
    # Drip profile covering Y = 36 to 56, X from -14 to +14
    pts = [
        FreeCAD.Vector(-12.8, 56.0, 0),
        FreeCAD.Vector(12.8, 56.0, 0),
        FreeCAD.Vector(14.2, 47.0, 0),
        FreeCAD.Vector(13.5, 41.0, 0),  # Right drip 1 tip
        FreeCAD.Vector(11.0, 44.5, 0),  # notch
        FreeCAD.Vector(8.5, 38.0, 0),   # Right drip 2 tip
        FreeCAD.Vector(5.5, 43.0, 0),   # notch
        FreeCAD.Vector(0.0, 35.5, 0),   # Center long drip tip
        FreeCAD.Vector(-4.5, 42.5, 0),  # notch
        FreeCAD.Vector(-7.5, 38.5, 0),  # Left drip 2 tip
        FreeCAD.Vector(-10.5, 43.0, 0), # notch
        FreeCAD.Vector(-13.0, 40.5, 0), # Left drip 1 tip
        FreeCAD.Vector(-14.2, 47.0, 0),
        FreeCAD.Vector(-12.8, 56.0, 0)
    ]
    wire = Part.Wire(Part.makePolygon(pts))
    face = Part.Face(wire)
    solid = face.extrude(FreeCAD.Vector(0, 0, h_drip))
    solid.translate(FreeCAD.Vector(0, 0, z_base))
    return solid

# 2. Test X-Patch Solid
def make_x_patch(cx, cy, size, bar_w, h, z_base):
    # Two rotated crossing bars
    b1 = Part.makeBox(size, bar_w, h)
    b1.translate(FreeCAD.Vector(-size/2.0, -bar_w/2.0, 0))
    b1.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 45)
    
    b2 = Part.makeBox(size, bar_w, h)
    b2.translate(FreeCAD.Vector(-size/2.0, -bar_w/2.0, 0))
    b2.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), -45)
    
    x_solid = b1.fuse(b2)
    # Fillet vertical edges of the X if possible
    x_solid.translate(FreeCAD.Vector(cx, cy, z_base))
    return x_solid

# 3. Test Stitches Solid
def make_raised_stitches(x1, y1, x2, y2, n_stitches, stitch_len, line_w, h, z_base):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx**2 + dy**2)
    ux, uy = dx/dist, dy/dist
    px, py = -uy, ux
    
    # Main curved or straight seam
    seam = Part.makeBox(dist, line_w, h)
    seam.translate(FreeCAD.Vector(0, -line_w/2.0, 0))
    angle = math.degrees(math.atan2(dy, dx))
    seam.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), angle)
    seam.translate(FreeCAD.Vector(x1, y1, z_base))
    
    solids = [seam]
    sl2 = stitch_len / 2.0
    for i in range(1, n_stitches + 1):
        t = i / float(n_stitches + 1)
        cx = x1 + dx * t
        cy = y1 + dy * t
        st = Part.makeBox(line_w * 1.2, stitch_len, h * 1.2)
        st.translate(FreeCAD.Vector(-line_w * 0.6, -sl2, 0))
        st.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), angle)
        st.translate(FreeCAD.Vector(cx, cy, z_base))
        solids.append(st)
        
    res = solids[0]
    for s in solids[1:]:
        res = res.fuse(s)
    return res

# 4. Test Broken Heart Solid
def make_broken_heart(cx, cy, size, h, z_base):
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
    heart.translate(FreeCAD.Vector(cx, cy, z_base))
    return heart

drip = make_drip_solid(0, 0.5)
x_patch = make_x_patch(6.0, 12.0, 6.0, 1.6, 0.5, 0)
stitches = make_raised_stitches(-3.0, 6.0, -8.0, 18.0, 4, 3.0, 0.7, 0.4, 0)
heart = make_broken_heart(-6.0, 12.0, 5.5, 0.5, 0)

obj1 = doc.addObject("Part::Feature", "Drip")
obj1.Shape = drip
obj2 = doc.addObject("Part::Feature", "XPatch")
obj2.Shape = x_patch
obj3 = doc.addObject("Part::Feature", "Stitches")
obj3.Shape = stitches
obj4 = doc.addObject("Part::Feature", "Heart")
obj4.Shape = heart

doc.recompute()
print("All features created successfully!")
FreeCAD.closeDocument("test_features")
