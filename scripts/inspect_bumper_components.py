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

pos6 = get_buffer(data['meshes'][6]['primitives'][0]['attributes']['POSITION'])
indices6 = get_buffer(data['meshes'][6]['primitives'][0]['indices']).flatten()

t6 = pos6[indices6].reshape(-1, 3, 3)
t6_c = t6.mean(axis=1)

# Check connected components of triangles in bumpers-trans
# Two triangles are connected if they share an edge
from collections import defaultdict
edge_to_tri = defaultdict(list)
for t_idx, (i0, i1, i2) in enumerate(indices6.reshape(-1, 3)):
    e1 = tuple(sorted((i0, i1)))
    e2 = tuple(sorted((i1, i2)))
    e3 = tuple(sorted((i2, i0)))
    edge_to_tri[e1].append(t_idx)
    edge_to_tri[e2].append(t_idx)
    edge_to_tri[e3].append(t_idx)

adj = defaultdict(set)
for edge, tri_list in edge_to_tri.items():
    if len(tri_list) > 1:
        for t1 in tri_list:
            for t2 in tri_list:
                if t1 != t2:
                    adj[t1].add(t2)

num_tris = len(indices6) // 3
visited = set()
components = []
for t in range(num_tris):
    if t not in visited:
        comp = []
        q = [t]
        visited.add(t)
        while q:
            curr = q.pop()
            comp.append(curr)
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    q.append(neighbor)
        components.append(comp)

print(f"Total connected components in bumpers-trans: {len(components)}")
for idx, comp in enumerate(components):
    comp_t = t6_c[comp]
    x_min, x_max = comp_t[:, 0].min(), comp_t[:, 0].max()
    y_min, y_max = comp_t[:, 1].min(), comp_t[:, 1].max()
    z_min, z_max = comp_t[:, 2].min(), comp_t[:, 2].max()
    print(f"Component {idx}: count={len(comp)} X=[{x_min:.2f}, {x_max:.2f}], Y=[{y_min:.2f}, {y_max:.2f}], Z=[{z_min:.2f}, {z_max:.2f}]")
