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

for mesh in gltf["meshes"]:
    if mesh["name"] == "abxy-buttons-trans":
        prim = mesh["primitives"][0]
        pos = get_accessor_data(prim["attributes"]["POSITION"])
        idx = get_accessor_data(prim["indices"])
        print(f"abxy-buttons-trans: pos count={len(pos)}, triangles={len(idx)//3}")

        # Let's find connected components!
        adj = {}
        triangles = idx.reshape(-1, 3)
        for t_i, (a, b, c) in enumerate(triangles):
            for v in (a, b, c):
                adj.setdefault(v, []).append(t_i)

        visited_triangles = set()
        components = []
        for t_i in range(len(triangles)):
            if t_i in visited_triangles:
                continue
            comp = []
            queue = [t_i]
            visited_triangles.add(t_i)
            while queue:
                curr = queue.pop()
                comp.append(curr)
                for v in triangles[curr]:
                    for neighbor in adj[v]:
                        if neighbor not in visited_triangles:
                            visited_triangles.add(neighbor)
                            queue.append(neighbor)
            components.append(comp)

        print(f"Total connected components: {len(components)}")
        for c_i, comp in enumerate(components):
            comp_indices = triangles[comp].flatten()
            c_pos = pos[comp_indices]
            min_pt = c_pos.min(axis=0)
            max_pt = c_pos.max(axis=0)
            center = c_pos.mean(axis=0)
            print(f"Component {c_i:2d}: tri_count={len(comp):4d}, center=({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}), min_z={min_pt[2]:.2f}, max_z={max_pt[2]:.2f}")
