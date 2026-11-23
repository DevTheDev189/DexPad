import FreeCAD
import Part
import math

doc = FreeCAD.newDocument("test_flush_fillet")

pts_coffin_r = [
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Vector(12.7, 0, 0),         # Foot corner
    FreeCAD.Vector(14.5, 36.0, 0),      # Lower flank
    FreeCAD.Vector(17.4, 41.5, 0),      # Primary bat wingtip flare
    FreeCAD.Vector(15.2, 44.0, 0),      # Wing scallop notch
    FreeCAD.Vector(16.2, 46.5, 0),      # Secondary winglet cusp
    FreeCAD.Vector(14.0, 49.5, 0),      # Upper shoulder
    FreeCAD.Vector(12.7, 56.0, 0),      # Head corner
    FreeCAD.Vector(0, 56.0, 0),         # Head center
]
pts_coffin_l = [FreeCAD.Vector(-p.x, p.y, 0) for p in reversed(pts_coffin_r[1:-1])]
all_pts_coffin = pts_coffin_r + pts_coffin_l + [pts_coffin_r[0]]
face_coffin = Part.Face(Part.Wire(Part.makePolygon(all_pts_coffin)))

h_case = 4.3
h_drip = 0.42
solid_case = face_coffin.extrude(FreeCAD.Vector(0, 0, h_case))

# Vertical corner fillets
vert_e = [e for e in solid_case.Edges if abs(e.Length - h_case) < 0.01]
solid_case = solid_case.makeFillet(1.4, vert_e)

# Lower perimeter fillet ONLY (Y <= 38.0 and foot at Y = 0)
# We do NOT fillet the top head (Y > 38.0) because the slime goes there!
lower_top_edges = [
    e for e in solid_case.Edges
    if abs(e.Vertexes[0].Point.z - h_case) < 0.01 and abs(e.Vertexes[1].Point.z - h_case) < 0.01
    and (e.Vertexes[0].Point.y <= 38.0 or e.Vertexes[1].Point.y <= 38.0)
    and (e.Vertexes[0].Point.y < 43.0 and e.Vertexes[1].Point.y < 43.0)
]
print("Lower top perimeter edges count:", len(lower_top_edges))
try:
    solid_case = solid_case.makeFillet(1.2, lower_top_edges)
    print("Lower deck rim fillet succeeded!")
except Exception as e:
    print("Lower deck rim fillet error:", e)

# Now create flush slime:
pts_slime = [
    FreeCAD.Vector(0, 56.0, 0),
    FreeCAD.Vector(12.7, 56.0, 0),
    FreeCAD.Vector(14.0, 49.5, 0),
    FreeCAD.Vector(16.2, 46.5, 0),
    FreeCAD.Vector(15.2, 44.0, 0),
]
def append_arc(cx, cy, r, a_start, a_end, n_steps=6):
    for i in range(n_steps + 1):
        t = i / float(n_steps)
        ang = math.radians(a_start + (a_end - a_start) * t)
        pts_slime.append(FreeCAD.Vector(cx + r * math.cos(ang), cy + r * math.sin(ang), 0))

# Drips
append_arc(13.2, 40.8, 1.4, 0, -180, 6)
append_arc(10.2, 43.5, 1.6, 0, 180, 5)
append_arc(7.2, 41.5, 1.5, 0, -180, 6)
append_arc(4.2, 44.5, 1.5, 0, 180, 5)
pts_slime.append(FreeCAD.Vector(1.4, 40.5, 0))
pts_slime.append(FreeCAD.Vector(1.6, 38.8, 0))
append_arc(0.0, 37.6, 1.6, 20, -200, 8)
pts_slime.append(FreeCAD.Vector(-1.6, 38.8, 0))
pts_slime.append(FreeCAD.Vector(-1.4, 40.5, 0))
append_arc(-3.8, 44.0, 1.5, 0, 180, 5)
append_arc(-6.8, 41.0, 1.5, 0, -180, 6)
append_arc(-9.8, 43.8, 1.5, 0, 180, 5)
append_arc(-12.6, 41.2, 1.4, 0, -180, 6)

pts_slime.append(FreeCAD.Vector(-15.2, 44.0, 0))
pts_slime.append(FreeCAD.Vector(-16.2, 46.5, 0))
pts_slime.append(FreeCAD.Vector(-14.0, 49.5, 0))
pts_slime.append(FreeCAD.Vector(-12.7, 56.0, 0))
pts_slime.append(FreeCAD.Vector(0, 56.0, 0))

w_slime = Part.Wire(Part.makePolygon(pts_slime))
solid_slime = Part.Face(w_slime).extrude(FreeCAD.Vector(0, 0, h_drip))

# Fillet vertical corners of slime matching the case vertical corners (R = 1.4 mm)
vert_slime = [e for e in solid_slime.Edges if abs(e.Length - h_drip) < 0.01 and (e.Vertexes[0].Point.y >= 44.0)]
if vert_slime:
    try:
        solid_slime = solid_slime.makeFillet(1.4, vert_slime)
        print("Slime vertical corner fillets succeeded!")
    except Exception as e:
        print("Slime vertical corner error:", e)

# Bevel the top outer rim of the slime (Y > 43.0 and head at Y = 56.0) with R = 1.2 mm matching the case!
slime_outer_rim = [
    e for e in solid_slime.Edges
    if abs(e.Vertexes[0].Point.z - h_drip) < 0.01 and abs(e.Vertexes[1].Point.z - h_drip) < 0.01
    and (e.Vertexes[0].Point.y >= 43.5 or e.Vertexes[1].Point.y >= 43.5)
]
print("Slime outer top rim edges:", len(slime_outer_rim))
try:
    solid_slime = solid_slime.makeFillet(1.2, slime_outer_rim)
    print("Slime outer rim fillet succeeded! (Matches case R=1.2 mm)")
except Exception as e:
    print("Slime outer rim fillet error:", e)

# And bevel the drip droplet bottom edge with soft R = 0.14 mm
drip_droplet_edges = [
    e for e in solid_slime.Edges
    if abs(e.Vertexes[0].Point.z - h_drip) < 0.01 and abs(e.Vertexes[1].Point.z - h_drip) < 0.01
    and (e.Vertexes[0].Point.y < 43.5 and e.Vertexes[1].Point.y < 43.5)
]
try:
    solid_slime = solid_slime.makeFillet(0.14, drip_droplet_edges)
    print("Slime droplet fillet succeeded!")
except Exception as e:
    print("Slime droplet fillet error:", e)

solid_slime.translate(FreeCAD.Vector(0, 0, h_case))
fused = solid_case.fuse(solid_slime)
print("Fused volume:", fused.Volume, "Solids:", len(fused.Solids))

FreeCAD.closeDocument("test_flush_fillet")
