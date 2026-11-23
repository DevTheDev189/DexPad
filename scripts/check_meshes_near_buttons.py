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
    name = mesh["name"]
    for prim in mesh["primitives"]:
        pos = get_accessor_data(prim["attributes"]["POSITION"])
        # Check if any vertices are in the button region (x in [2, 6], y in [1, 5], z > 0)
        in_region = (pos[:,0] >= 2.0) & (pos[:,0] <= 6.0) & (pos[:,1] >= 1.0) & (pos[:,1] <= 5.0) & (pos[:,2] > 0)
        if np.any(in_region):
            print(f"Mesh '{name}' has {np.sum(in_region)} vertices in button region (total={len(pos)})")
