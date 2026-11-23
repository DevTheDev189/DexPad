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

# Let's map out exactly which triangles belong to which button and which part
# Buttons:
# A: base = Comp 1, letters = Comps 4, 5, 6
# B: base = Comp 0, letters = Comps 7, 8, 9, 10, 11
# X: base = Comp 2, letters = Comps 14, 15
# Y: base = Comp 3, letters = Comps 12, 13

buttons = {
    'A': {'base': [1], 'letter': [4, 5, 6]},
    'B': {'base': [0], 'letter': [7, 8, 9, 10, 11]},
    'X': {'base': [2], 'letter': [14, 15]},
    'Y': {'base': [3], 'letter': [12, 13]},
}

for btn_name, parts in buttons.items():
    base_tris = [t for c in parts['base'] for t in components[c]]
    letter_tris = [t for c in parts['letter'] for t in components[c]]
    base_idx = triangles[base_tris].flatten()
    letter_idx = triangles[letter_tris].flatten()
    base_pos = pos[base_idx]
    letter_pos = pos[letter_idx]
    print(f"Button {btn_name}:")
    print(f"  Base Z range: [{base_pos[:,2].min():.4f}, {base_pos[:,2].max():.4f}], mean={base_pos[:,2].mean():.4f}")
    print(f"  Letter Z range: [{letter_pos[:,2].min():.4f}, {letter_pos[:,2].max():.4f}], mean={letter_pos[:,2].mean():.4f}")
    print(f"  Protrusion above base max: {letter_pos[:,2].max() - base_pos[:,2].max():.4f}")
