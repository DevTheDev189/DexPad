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

# Find boundary edges of body-top-case around the hole
# An edge is a boundary edge if it belongs to only 1 triangle
from collections import defaultdict
edge_count = defaultdict(int)
for i in range(0, len(indices0), 3):
    i0, i1, i2 = indices0[i], indices0[i+1], indices0[i+2]
    e1 = tuple(sorted((i0, i1)))
    e2 = tuple(sorted((i1, i2)))
    e3 = tuple(sorted((i2, i0)))
    edge_count[e1] += 1
    edge_count[e2] += 1
    edge_count[e3] += 1

boundary_verts = set()
for edge, count in edge_count.items():
    if count == 1:
        boundary_verts.add(edge[0])
        boundary_verts.add(edge[1])

bv_pos = pos0[list(boundary_verts)]
hole_bv = bv_pos[(np.abs(bv_pos[:, 0]) < 1.0) & (bv_pos[:, 1] > 3.0) & (bv_pos[:, 1] < 4.5) & (bv_pos[:, 2] > 0.5)]

print(f"Found {len(hole_bv)} boundary vertices around the home button hole:")
center_x = (hole_bv[:,0].min() + hole_bv[:,0].max()) / 2.0
center_y = (hole_bv[:,1].min() + hole_bv[:,1].max()) / 2.0
center_z = (hole_bv[:,2].min() + hole_bv[:,2].max()) / 2.0

rad_x = (hole_bv[:,0].max() - hole_bv[:,0].min()) / 2.0
rad_y = (hole_bv[:,1].max() - hole_bv[:,1].min()) / 2.0
rad_z = (hole_bv[:,2].max() - hole_bv[:,2].min()) / 2.0

print(f"Hole center: X={center_x:.4f}, Y={center_y:.4f}, Z={center_z:.4f}")
print(f"Hole radius: X_rad={rad_x:.4f}, Y_rad={rad_y:.4f}, Z_span={rad_z:.4f}")
print(f"Hole bounds: X=[{hole_bv[:,0].min():.3f}, {hole_bv[:,0].max():.3f}], Y=[{hole_bv[:,1].min():.3f}, {hole_bv[:,1].max():.3f}], Z=[{hole_bv[:,2].min():.3f}, {hole_bv[:,2].max():.3f}]")
