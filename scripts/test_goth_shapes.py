import FreeCAD
import Part
import math

# Test parametric shapes:
# 1. Bat wing silhouette
def make_bat_cutter(center_x, center_y, width, height, depth, z_top):
    # Half-width and half-height
    w2 = width / 2.0
    h2 = height / 2.0
    
    # Points defining the right half of the bat:
    # (x, y) relative to center
    pts_r = [
        FreeCAD.Vector(0.0, h2 * 0.5, 0),         # top center notch between ears
        FreeCAD.Vector(w2 * 0.12, h2 * 0.9, 0),   # right ear tip
        FreeCAD.Vector(w2 * 0.22, h2 * 0.4, 0),   # ear base
        FreeCAD.Vector(w2 * 0.55, h2 * 0.8, 0),   # top wing arch 1
        FreeCAD.Vector(w2 * 1.0, h2 * 1.0, 0),    # wing top tip
        FreeCAD.Vector(w2 * 0.85, h2 * 0.3, 0),   # scallop tip 1
        FreeCAD.Vector(w2 * 0.70, h2 * 0.45, 0),  # scallop cusp 1
        FreeCAD.Vector(w2 * 0.55, -h2 * 0.2, 0),  # scallop tip 2
        FreeCAD.Vector(w2 * 0.40, 0.0, 0),        # scallop cusp 2
        FreeCAD.Vector(w2 * 0.25, -h2 * 0.6, 0),  # scallop tip 3
        FreeCAD.Vector(w2 * 0.12, -h2 * 0.3, 0),  # bottom body join
        FreeCAD.Vector(0.0, -h2 * 0.8, 0)         # tail tip
    ]
    
    # Mirror for left half:
    pts_l = [FreeCAD.Vector(-p.x, p.y, 0) for p in reversed(pts_r[1:-1])]
    
    all_pts = pts_r + pts_l + [pts_r[0]]
    wire = Part.Wire(Part.makePolygon(all_pts))
    face = Part.Face(wire)
    solid = face.extrude(FreeCAD.Vector(0, 0, depth + 0.1))
    solid.translate(FreeCAD.Vector(center_x, center_y, z_top - depth))
    return solid

# 2. Frankenstein stitched scar
def make_stitched_scar(x1, y1, x2, y2, num_stitches, stitch_len, line_w, depth, z_top):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx**2 + dy**2)
    ux = dx / dist
    uy = dy / dist
    # Perpendicular unit vector
    px = -uy
    py = ux
    
    solids = []
    # Main cut line
    # Create polygon for main cut line
    lw2 = line_w / 2.0
    pts_main = [
        FreeCAD.Vector(x1 - px*lw2, y1 - py*lw2, 0),
        FreeCAD.Vector(x2 - px*lw2, y2 - py*lw2, 0),
        FreeCAD.Vector(x2 + px*lw2, y2 + py*lw2, 0),
        FreeCAD.Vector(x1 + px*lw2, y1 + py*lw2, 0),
        FreeCAD.Vector(x1 - px*lw2, y1 - py*lw2, 0)
    ]
    w_main = Part.Wire(Part.makePolygon(pts_main))
    f_main = Part.Face(w_main)
    s_main = f_main.extrude(FreeCAD.Vector(0, 0, depth + 0.1))
    s_main.translate(FreeCAD.Vector(0, 0, z_top - depth))
    solids.append(s_main)
    
    # Cross stitches
    sl2 = stitch_len / 2.0
    for i in range(1, num_stitches + 1):
        t = i / float(num_stitches + 1)
        cx = x1 + dx * t
        cy = y1 + dy * t
        
        # Cross stitch bar (perpendicular to main cut)
        pts_cross = [
            FreeCAD.Vector(cx - px*sl2 - ux*lw2, cy - py*sl2 - uy*lw2, 0),
            FreeCAD.Vector(cx + px*sl2 - ux*lw2, cy + py*sl2 - uy*lw2, 0),
            FreeCAD.Vector(cx + px*sl2 + ux*lw2, cy + py*sl2 + uy*lw2, 0),
            FreeCAD.Vector(cx - px*sl2 + ux*lw2, cy - py*sl2 + uy*lw2, 0),
            FreeCAD.Vector(cx - px*sl2 - ux*lw2, cy - py*sl2 - uy*lw2, 0)
        ]
        w_cross = Part.Wire(Part.makePolygon(pts_cross))
        f_cross = Part.Face(w_cross)
        s_cross = f_cross.extrude(FreeCAD.Vector(0, 0, depth + 0.1))
        s_cross.translate(FreeCAD.Vector(0, 0, z_top - depth))
        solids.append(s_cross)
        
    combined = solids[0]
    for s in solids[1:]:
        combined = combined.fuse(s)
    return combined

# 3. Broken Heart motif
def make_broken_heart(center_x, center_y, size, depth, z_top):
    # Parametric heart with a zigzag crack down the middle
    # Left half and right half slightly separated by a 0.35 mm zigzag cut
    s2 = size / 2.0
    # Left half points
    pts_left = [
        FreeCAD.Vector(-0.2, s2 * 0.4, 0),    # top cleft left edge
        FreeCAD.Vector(-s2 * 0.5, s2 * 0.9, 0),# left hump top
        FreeCAD.Vector(-s2 * 0.9, s2 * 0.5, 0),# left hump outer
        FreeCAD.Vector(-s2 * 0.7, -s2 * 0.2, 0),# lower left slope
        FreeCAD.Vector(-0.2, -s2 * 0.9, 0),   # bottom point left
        # Zigzag crack going back up:
        FreeCAD.Vector(-0.4, -s2 * 0.4, 0),
        FreeCAD.Vector(-0.1, -s2 * 0.0, 0),
        FreeCAD.Vector(-0.35, s2 * 0.2, 0),
        FreeCAD.Vector(-0.2, s2 * 0.4, 0)
    ]
    w_l = Part.Wire(Part.makePolygon(pts_left))
    f_l = Part.Face(w_l)
    s_l = f_l.extrude(FreeCAD.Vector(0, 0, depth + 0.1))
    
    # Right half points (shifted slightly by +0.3 mm for broken look):
    pts_right = [
        FreeCAD.Vector(0.2, s2 * 0.4 + 0.2, 0),
        FreeCAD.Vector(0.35, s2 * 0.2 + 0.2, 0),
        FreeCAD.Vector(0.1, -s2 * 0.0 + 0.2, 0),
        FreeCAD.Vector(0.4, -s2 * 0.4 + 0.2, 0),
        FreeCAD.Vector(0.2, -s2 * 0.9 + 0.2, 0),
        FreeCAD.Vector(s2 * 0.7, -s2 * 0.2 + 0.2, 0),
        FreeCAD.Vector(s2 * 0.9, s2 * 0.5 + 0.2, 0),
        FreeCAD.Vector(s2 * 0.5, s2 * 0.9 + 0.2, 0),
        FreeCAD.Vector(0.2, s2 * 0.4 + 0.2, 0)
    ]
    w_r = Part.Wire(Part.makePolygon(pts_right))
    f_r = Part.Face(w_r)
    s_r = f_r.extrude(FreeCAD.Vector(0, 0, depth + 0.1))
    
    heart = s_l.fuse(s_r)
    heart.translate(FreeCAD.Vector(center_x, center_y, z_top - depth))
    return heart

# Test building all three
bat = make_bat_cutter(12.45, 25.0, 10.0, 4.5, 0.25, 4.0)
scar = make_stitched_scar(14.0, 10.0, 20.0, 17.0, 4, 2.0, 0.4, 0.25, 4.0)
heart = make_broken_heart(7.0, 13.0, 5.0, 0.25, 4.0)

print("Bat volume:", bat.Volume, "Valid:", bat.isValid())
print("Scar volume:", scar.Volume, "Valid:", scar.isValid())
print("Heart volume:", heart.Volume, "Valid:", heart.isValid())
