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
prim = mesh["primitives"][0]
pos = get_accessor_data(prim["attributes"]["POSITION"])
idx = get_accessor_data(prim["indices"])
triangles = idx.reshape(-1, 3)

# In inspect_abxy_components.py, we found 16 connected components:
# Let's inspect the z coordinates and bounding boxes of the 4 bases vs their letters:
# Base A = Comp 1: z in [0.85, 1.68]
# Letter A = Comp 4, 5, 6: z in [1.36, 1.88]
# Notice how Letter A has z from 1.36 to 1.88, while Base A top is 1.68.
# In the original 3D asset, the letter is an embossed 3D geometry resting on top of the cylinder!
print("Comp 1 (Base A):", pos[triangles[comp_indices if 'comp_indices' in locals() else 0]].min(axis=0))
