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

# Check abxy-buttons-trans (Mesh 10) and abxy-buttons-exterior-trans (Mesh 11)
pos10 = get_buffer(data['meshes'][10]['primitives'][0]['attributes']['POSITION'])
indices10 = get_buffer(data['meshes'][10]['primitives'][0]['indices']).flatten()

pos11 = get_buffer(data['meshes'][11]['primitives'][0]['attributes']['POSITION'])
indices11 = get_buffer(data['meshes'][11]['primitives'][0]['indices']).flatten()

print(f"Mesh 10 count={len(pos10)}, Z range: [{pos10[:,2].min():.3f}, {pos10[:,2].max():.3f}]")
print(f"Mesh 11 count={len(pos11)}, Z range: [{pos11[:,2].min():.3f}, {pos11[:,2].max():.3f}]")

# Let's inspect connected components of Mesh 10:
from collections import defaultdict
edge_to_tri = defaultdict(list)
for t_idx, (i0, i1, i2) in enumerate(indices10.reshape(-1, 3)):
    for e in [(min(i0,i1), max(i0,i1)), (min(i1,i2), max(i1,i2)), (min(i2,i0), max(i2,i0))]:
        edge_to_tri[e].append(t_idx)

adj = defaultdict(set)
for e, t_list in edge_to_tri.items():
    if len(t_list) > 1:
        for t1 in t_list:
            for t2 in t_list:
                if t1 != t2:
                    adj[t1].add(t2)

num_tris = len(indices10) // 3
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
            for nbr in adj[curr]:
                if nbr not in visited:
                    visited.add(nbr)
                    q.append(nbr)
        components.append(comp)

t10 = pos10[indices10].reshape(-1, 3, 3)
t10_c = t10.mean(axis=1)

print(f"Total connected components in abxy-buttons-trans: {len(components)}")
for idx, comp in enumerate(components):
    comp_t = t10_c[comp]
    print(f"Comp {idx}: count={len(comp)}, X=[{comp_t[:,0].min():.2f}, {comp_t[:,0].max():.2f}], Y=[{comp_t[:,1].min():.2f}, {comp_t[:,1].max():.2f}], Z=[{comp_t[:,2].min():.2f}, {comp_t[:,2].max():.2f}]")
