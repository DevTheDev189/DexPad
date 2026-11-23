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

tri_count = len(triangles)
adj = [[] for _ in range(len(pos))]
for t in range(tri_count):
    a, b, c = triangles[t]
    adj[a].append(t)
    adj[b].append(t)
    adj[c].append(t)

visited = [False] * tri_count
components = []
for t in range(tri_count):
    if visited[t]:
        continue
    comp = []
    queue = [t]
    visited[t] = True
    while queue:
        curr = queue.pop()
        comp.append(curr)
        for v in triangles[curr]:
            for nbr in adj[v]:
                if not visited[nbr]:
                    visited[nbr] = True
                    queue.append(nbr)
    components.append(comp)

btn_parts = {'a': {'base': [], 'letter': []}, 'b': {'base': [], 'letter': []}, 'x': {'base': [], 'letter': []}, 'y': {'base': [], 'letter': []}}

for comp in components:
    c_tris = triangles[comp].flatten()
    c_pos = pos[c_tris]
    mean_x = float(c_pos[:,0].mean())
    mean_y = float(c_pos[:,1].mean())
    tri_len = len(comp)

    if mean_y < 2.0:
        btn = 'a'
    elif mean_x > 4.5:
        btn = 'b'
    elif mean_x < 3.5:
        btn = 'x'
    else:
        btn = 'y'

    is_base = (tri_len == 750 or tri_len == 652) and c_pos[:,2].max() < 1.7
    if is_base:
        btn_parts[btn]['base'].extend(comp)
    else:
        btn_parts[btn]['letter'].extend(comp)

for btn, parts in btn_parts.items():
    base_tris = triangles[parts['base']].flatten()
    letter_tris = triangles[parts['letter']].flatten()
    max_base_z = pos[base_tris][:,2].max()
    print(f"=== Button {btn.upper()} ===")
    print(f"Base max Z: {max_base_z:.4f}")
    letter_pts = pos[letter_tris]
    print(f"Letter original Z range: [{letter_pts[:,2].min():.4f}, {letter_pts[:,2].max():.4f}]")
    
    # Test formula:
    # dz = z - max_base_z
    # if dz > 0: max_base_z + dz * 0.20 + 0.016
    # else: max_base_z + dz * 0.10 + 0.010
    new_z = np.where(
        letter_pts[:,2] > max_base_z,
        max_base_z + (letter_pts[:,2] - max_base_z) * 0.20 + 0.016,
        max_base_z + (letter_pts[:,2] - max_base_z) * 0.10 + 0.010
    )
    print(f"Letter NEW Z range: [{new_z.min():.4f}, {new_z.max():.4f}]")
    print(f"Letter is above base: min new_z - max_base_z = {new_z.min() - max_base_z:.4f}, max new_z - max_base_z = {new_z.max() - max_base_z:.4f}")
