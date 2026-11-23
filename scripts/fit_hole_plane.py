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

pos0 = get_buffer(data['meshes'][0]['primitives'][0]['attributes']['POSITION'])
indices0 = get_buffer(data['meshes'][0]['primitives'][0]['indices']).flatten()

from collections import defaultdict
edge_count = defaultdict(int)
for i in range(0, len(indices0), 3):
    i0, i1, i2 = indices0[i], indices0[i+1], indices0[i+2]
    edge_count[tuple(sorted((i0, i1)))] += 1
    edge_count[tuple(sorted((i1, i2)))] += 1
    edge_count[tuple(sorted((i2, i0)))] += 1

boundary_verts = [v for edge, count in edge_count.items() if count == 1 for v in edge]
bv_pos = pos0[boundary_verts]
hole_bv = bv_pos[(np.abs(bv_pos[:, 0]) < 1.0) & (bv_pos[:, 1] > 3.0) & (bv_pos[:, 1] < 4.5) & (bv_pos[:, 2] > 0.5)]

# Fit plane to hole_bv using SVD
centroid = hole_bv.mean(axis=0)
u, s, vh = np.linalg.svd(hole_bv - centroid)
normal = vh[2] # normal is last singular vector
if normal[2] < 0: # make it point towards camera (+Z)
    normal = -normal

print(f"Hole Centroid: X={centroid[0]:.4f}, Y={centroid[1]:.4f}, Z={centroid[2]:.4f}")
print(f"Fitted Normal: {normal}")
angle_x = np.arctan2(normal[1], normal[2])
print(f"Tilt angle around X-axis: {angle_x:.4f} rad ({np.degrees(angle_x):.2f} deg)")
