import struct
import json
import numpy as np

with open("app/public/models/xbox_elite.glb", "rb") as f:
    f.seek(12)
    chunk_len = int.from_bytes(f.read(4), 'little')
    f.seek(20)
    gltf = json.loads(f.read(chunk_len).decode('utf-8'))
    f.seek(20 + chunk_len)
    bin_len = int.from_bytes(f.read(4), 'little')
    f.seek(28 + chunk_len)
    bin_data = f.read(bin_len)

def get_accessor_data(acc_idx):
    acc = gltf["accessors"][acc_idx]
    buff_view = gltf["bufferViews"][acc["bufferView"]]
    offset = buff_view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    type_map = {"VEC3": 3, "SCALAR": 1, "VEC2": 2}
    n = type_map[acc["type"]]
    comp_map = {5126: "f", 5123: "H", 5125: "I"}
    fmt = "<" + str(n) + comp_map[acc["componentType"]]
    elem_size = struct.calcsize(fmt)
    data = []
    for i in range(count):
        val = struct.unpack_from(fmt, bin_data, offset + i * elem_size)
        data.append(val if n > 1 else val[0])
    return np.array(data)

mesh = gltf["meshes"][0] # body-top-case
pos = get_accessor_data(mesh["primitives"][0]["attributes"]["POSITION"])

# Find vertices around the hole (x in [-0.8, 0.8], y in [3.5, 4.8], z in [0.4, 1.4])
mask = (np.abs(pos[:,0]) < 0.8) & (pos[:,1] > 3.6) & (pos[:,1] < 4.6) & (pos[:,2] > 0.4) & (pos[:,2] < 1.4)
hole_pts = pos[mask]
print(f"Hole points count: {len(hole_pts)}")

# Filter points near the rim (distance from centroid in xy projection)
# Current jewel is at (0, 4.11, 0.90)
center = np.array([0.0, 4.11, 0.90])
dists = np.linalg.norm(hole_pts - center, axis=1)
print(f"Distances to (0, 4.11, 0.90): min={dists.min():.4f}, 10th={np.percentile(dists, 10):.4f}, median={np.median(dists):.4f}")

# Look at rim points (dists between 0.45 and 0.65)
rim_mask = (dists >= 0.45) & (dists <= 0.65)
rim_pts = hole_pts[rim_mask]
print(f"Rim points count: {len(rim_pts)}")
print(f"Rim bounds: X=[{rim_pts[:,0].min():.4f}, {rim_pts[:,0].max():.4f}], Y=[{rim_pts[:,1].min():.4f}, {rim_pts[:,1].max():.4f}], Z=[{rim_pts[:,2].min():.4f}, {rim_pts[:,2].max():.4f}]")
print(f"Rim centroid: {rim_pts.mean(axis=0)}")

# Let's find the radius from rim centroid:
rim_center = rim_pts.mean(axis=0)
rim_dists = np.linalg.norm(rim_pts - rim_center, axis=1)
print(f"Rim radius from its centroid: min={rim_dists.min():.4f}, mean={rim_dists.mean():.4f}, max={rim_dists.max():.4f}")
