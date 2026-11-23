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
    base_pts = pos[base_tris]
    letter_pts = pos[letter_tris]
    base_max = base_pts[:,2].max()
    letter_max = letter_pts[:,2].max()
    protrusion = letter_max - base_max
    
    # If we want a sleek low-profile 0.04 protrusion:
    # We want letter_max to be base_max + 0.04:
    shift = protrusion - 0.04
    print(f"Button {btn.upper()}: original protrusion={protrusion:.4f}, shift needed={shift:.4f}")
    new_max = letter_max - shift
    print(f"  -> New max Z: {new_max:.4f} (base_max + {new_max - base_max:.4f})")
