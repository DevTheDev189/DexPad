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

mesh = [m for m in gltf["meshes"] if m["name"] == "combined-noncustom"][0]
pos = get_accessor_data(mesh["primitives"][0]["attributes"]["POSITION"])
print(f"combined-noncustom: min={pos.min(axis=0)}, max={pos.max(axis=0)}, count={len(pos)}")

# What about internal-components in the button region?
mesh_int = [m for m in gltf["meshes"] if m["name"] == "internal-components"][0]
pos_int = get_accessor_data(mesh_int["primitives"][0]["attributes"]["POSITION"])
in_abxy = (pos_int[:,0] > 2.5) & (pos_int[:,0] < 5.5) & (pos_int[:,1] > 1.0) & (pos_int[:,1] < 4.5) & (pos_int[:,2] > 0.5)
print(f"internal-components in abxy visible z > 0.5: count={np.sum(in_abxy)}")
if np.sum(in_abxy) > 0:
    print(f"max z of internal-components in abxy: {pos_int[in_abxy][:,2].max()}")
