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

# Let's inspect mesh 10 (abxy-buttons-trans)
mesh = [m for m in gltf["meshes"] if m["name"] == "abxy-buttons-trans"][0]
prim = mesh["primitives"][0]
pos = get_accessor_data(prim["attributes"]["POSITION"])
norm = get_accessor_data(prim["attributes"]["NORMAL"])
uv = get_accessor_data(prim["attributes"]["TEXCOORD_0"])
idx = get_accessor_data(prim["indices"])
triangles = idx.reshape(-1, 3)

# Let's check each component of abxy-buttons-trans
# In previous script:
# Comp 1: base of A (750 tris)
# Comp 0: base of B (750 tris)
# Comp 2: base of X (652 tris)
# Comp 3: base of Y (750 tris)

print(f"Normals min={norm.min(axis=0)}, max={norm.max(axis=0)}")
print(f"UV min={uv.min(axis=0)}, max={uv.max(axis=0)}")
