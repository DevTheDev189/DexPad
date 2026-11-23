import struct
import json
import numpy as np

with open('app/public/models/xbox_elite.glb', 'rb') as f:
    magic, version, length = struct.unpack('<4sII', f.read(12))
    chunk_len, chunk_type = struct.unpack('<I4s', f.read(8))
    json_bytes = f.read(chunk_len)
    data = json.loads(json_bytes.decode('utf-8'))
    bin_chunk_len, bin_chunk_type = struct.unpack('<I4s', f.read(8))
    bin_data = f.read(bin_chunk_len)

def get_buffer(accessor_idx):
    acc = data['accessors'][accessor_idx]
    bv = data['bufferViews'][acc['bufferView']]
    offset = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    count = acc['count']
    ctype = acc['componentType']
    type_ = acc['type']
    dtype = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}[ctype]
    num_components = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[type_]
    stride = bv.get('byteStride', dtype().itemsize * num_components)
    raw = bin_data[offset : offset + count * stride]
    return np.frombuffer(raw, dtype=dtype).reshape(count, num_components)

mesh = data['meshes'][10] # abxy-buttons-trans
pos = get_buffer(mesh['primitives'][0]['attributes']['POSITION'])
indices = get_buffer(mesh['primitives'][0]['indices']).flatten()

tri_centers = (pos[indices[0::3]] + pos[indices[1::3]] + pos[indices[2::3]]) / 3.0

print(f"Total triangles in abxy-buttons-trans: {len(tri_centers)}")

# Cluster by connected components or kmeans
# Let's inspect where the 4 button centers are:
# Typically:
# A is bottom: lowest Y
# Y is top: highest Y
# X is left: lowest X (between Y min and max)
# B is right: highest X
a_tris = tri_centers[tri_centers[:, 1] < 2.0]
y_tris = tri_centers[tri_centers[:, 1] > 3.2]
mid_y = (tri_centers[:, 1] >= 2.0) & (tri_centers[:, 1] <= 3.2)
x_tris = tri_centers[mid_y & (tri_centers[:, 0] < 3.9)]
b_tris = tri_centers[mid_y & (tri_centers[:, 0] >= 3.9)]

print("A tris:", len(a_tris), "center:", a_tris.mean(axis=0) if len(a_tris) else None)
print("B tris:", len(b_tris), "center:", b_tris.mean(axis=0) if len(b_tris) else None)
print("X tris:", len(x_tris), "center:", x_tris.mean(axis=0) if len(x_tris) else None)
print("Y tris:", len(y_tris), "center:", y_tris.mean(axis=0) if len(y_tris) else None)
