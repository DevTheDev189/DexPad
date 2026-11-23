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

# Filter for Button A in previous implementation:
# button_a_base: y < 2.0 && z <= 1.65
# button_a_letter: y < 2.0 && z > 1.65
for t_i, (a, b, c) in enumerate(triangles):
    cx = (pos[a][0] + pos[b][0] + pos[c][0]) / 3
    cy = (pos[a][1] + pos[b][1] + pos[c][1]) / 3
    cz = (pos[a][2] + pos[b][2] + pos[c][2]) / 3
    if cy < 2.0:
        pass

# Let's check which connected components are in Button A, B, X, Y
# In earlier component analysis:
# Comp 1: base of A (750 tris)
# Comp 4, 5, 6: letter of A (500 + 869 + 76 = 1445 tris)
# Comp 0: base of B (750 tris)
# Comp 7, 8, 9, 10, 11: letter of B
# Comp 2: base of X (652 tris)
# Comp 14, 15: letter of X
# Comp 3: base of Y (750 tris)
# Comp 12, 13: letter of Y

print("Component mapping to buttons:")
# Check sum of tris for each:
print("Total triangles in mesh:", len(triangles))
base_a_tris = 750
letter_a_tris = 500 + 869 + 76
base_b_tris = 750
letter_b_tris = 1381 + 498 + 516 + 476 + 204
base_x_tris = 652
letter_x_tris = 941 + 668
base_y_tris = 750
letter_y_tris = 963 + 628
total = base_a_tris + letter_a_tris + base_b_tris + letter_b_tris + base_x_tris + letter_x_tris + base_y_tris + letter_y_tris
print(f"Sum of component triangles: {total}")
