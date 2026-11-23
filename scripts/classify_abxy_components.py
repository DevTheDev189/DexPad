import struct
import json
import numpy as np

with open("app/public/models/xbox_elite.glb", "rb") as f:
    f.seek(12)
    chunk_len, chunk_type = struct.unpack("<I4s", f.read(8))
    gltf = json.loads(f.read(chunk_len).decode("utf-8"))
    bin_len, bin_type = struct.unpack("<I4s", f.read(8))
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

mesh = [m for m in gltf["meshes"] if m["name"] == "abxy-buttons-trans"][0]
pos = get_accessor_data(mesh["primitives"][0]["attributes"]["POSITION"])
idx = get_accessor_data(mesh["primitives"][0]["indices"])
triangles = idx.reshape(-1, 3)

adj = {}
for t_i, (a, b, c) in enumerate(triangles):
    for v in (a, b, c):
        adj.setdefault(v, []).append(t_i)

visited = set()
components = []
for t_i in range(len(triangles)):
    if t_i in visited:
        continue
    comp = []
    queue = [t_i]
    visited.add(t_i)
    while queue:
        curr = queue.pop()
        comp.append(curr)
        for v in triangles[curr]:
            for neighbor in adj[v]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    components.append(comp)

# Let's print each component's centroid and triangle count:
button_map = {}
for c_i, comp in enumerate(components):
    comp_tris = triangles[comp].flatten()
    c_pos = pos[comp_tris]
    mean_pt = c_pos.mean(axis=0)
    # Determine button:
    # A is around y=1.7, x=3.9
    # B is around y=2.6, x=5.0
    # X is around y=2.7, x=2.9
    # Y is around y=3.7, x=3.9
    if mean_pt[1] < 2.0:
        btn = 'A'
    elif mean_pt[0] > 4.5:
        btn = 'B'
    elif mean_pt[0] < 3.5:
        btn = 'X'
    else:
        btn = 'Y'
    is_base = (len(comp) == 750 or len(comp) == 652) and c_pos[:,2].max() < 1.7
    print(f"Comp {c_i:2d}: Button {btn}, {'BASE  ' if is_base else 'LETTER'}, tris={len(comp):4d}, center=({mean_pt[0]:.2f}, {mean_pt[1]:.2f}, {mean_pt[2]:.2f}), z=[{c_pos[:,2].min():.2f}, {c_pos[:,2].max():.2f}]")
