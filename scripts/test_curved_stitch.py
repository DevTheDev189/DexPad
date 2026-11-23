import FreeCAD
import Part
import math

doc = FreeCAD.newDocument("test_curved_stitch")

def make_curved_stitches(p0, p_ctrl, p1, n_stitches, stitch_len, line_w, h, z_base):
    # Quadratic Bezier curve
    def bezier_pt(t):
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p_ctrl[0] + t**2 * p1[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p_ctrl[1] + t**2 * p1[1]
        return x, y
    
    def bezier_tangent(t):
        dx = 2*(1-t)*(p_ctrl[0] - p0[0]) + 2*t*(p1[0] - p_ctrl[0])
        dy = 2*(1-t)*(p_ctrl[1] - p0[1]) + 2*t*(p1[1] - p_ctrl[1])
        mag = math.sqrt(dx**2 + dy**2)
        return dx/mag, dy/mag

    # Build seam as a sequence of small segments
    n_seam_segs = 16
    pts_seam = [bezier_pt(i / float(n_seam_segs)) for i in range(n_seam_segs + 1)]
    
    seam_solids = []
    for i in range(n_seam_segs):
        x_a, y_a = pts_seam[i]
        x_b, y_b = pts_seam[i+1]
        dx = x_b - x_a
        dy = y_b - y_a
        d = math.sqrt(dx**2 + dy**2)
        ang = math.degrees(math.atan2(dy, dx))
        seg = Part.makeBox(d + 0.1, line_w, h * 0.8)
        seg.translate(FreeCAD.Vector(0, -line_w/2.0, 0))
        seg.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), ang)
        seg.translate(FreeCAD.Vector(x_a, y_a, z_base))
        seam_solids.append(seg)
        
    full_seam = seam_solids[0]
    for s in seam_solids[1:]:
        full_seam = full_seam.fuse(s)

    # Cross stitches along curve
    cross_solids = []
    sl2 = stitch_len / 2.0
    for i in range(1, n_stitches + 1):
        t = i / float(n_stitches + 1)
        cx, cy = bezier_pt(t)
        tx, ty = bezier_tangent(t)
        # Normal vector is (-ty, tx)
        ang_tangent = math.degrees(math.atan2(ty, tx))
        ang_cross = ang_tangent + 90.0 # perpendicular to seam
        
        st = Part.makeBox(stitch_len, line_w * 1.35, h)
        st.translate(FreeCAD.Vector(-sl2, -line_w * 0.675, 0))
        # Fillet pill ends
        ve = [e for e in st.Edges if abs(e.Length - h) < 0.01 and (abs(e.Vertexes[0].Point.x - sl2) < 0.01 or abs(e.Vertexes[0].Point.x + sl2) < 0.01)]
        if len(ve) == 4:
            try:
                st = st.makeFillet(line_w * 0.55, ve)
            except Exception:
                pass
        # Fillet top rim
        top_e = [e for e in st.Edges if abs(e.Vertexes[0].Point.z - h) < 0.01 and abs(e.Vertexes[1].Point.z - h) < 0.01]
        try:
            st = st.makeFillet(0.08, top_e)
        except Exception:
            pass
            
        st.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), ang_cross)
        st.translate(FreeCAD.Vector(cx, cy, z_base))
        cross_solids.append(st)
        
    res = full_seam
    for s in cross_solids:
        res = res.fuse(s)
    return res

stitch = make_curved_stitches((1.5, 4.5), (5.5, 12.0), (11.5, 20.0), 5, 4.2, 0.9, 0.45, 0)
print("Curved stitch volume:", stitch.Volume)
obj = doc.addObject("Part::Feature", "Stitch")
obj.Shape = stitch
doc.recompute()
FreeCAD.closeDocument("test_curved_stitch")
