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
pos12 = get_buffer(data['meshes'][12]['primitives'][0]['attributes']['POSITION'])

# Filter vertices near X ~ 0, Y ~ 3.48
v0 = pos0[(np.abs(pos0[:, 0]) < 0.6) & (pos0[:, 1] > 3.0) & (pos0[:, 1] < 4.0)]
v12 = pos12[(np.abs(pos12[:, 0]) < 0.6) & (pos12[:, 1] > 3.0) & (pos12[:, 1] < 4.0)]

print(f"body-top-case cutout Z range: [{v0[:,2].min():.3f}, {v0[:,2].max():.3f}]")
print(f"lights-trans jewel Z range: [{v12[:,2].min():.3f}, {v12[:,2].max():.3f}]")
print(f"lights-trans jewel Y range: [{v12[:,1].min():.3f}, {v12[:,1].max():.3f}]")
print(f"lights-trans jewel X range: [{v12[:,0].min():.3f}, {v12[:,0].max():.3f}]")

# What does lights-trans contain at Y > 3.0?
print("\nTriangles / structure in lights-trans:")
indices12 = get_buffer(data['meshes'][12]['primitives'][0]['indices']).flatten()
tris12 = pos12[indices12].reshape(-1, 3, 3)
tris_center = tris12.mean(axis=1)
jewel_tris = tris12[(np.abs(tris_center[:, 0]) < 0.6) & (tris_center[:, 1] > 3.0) & (tris_center[:, 1] < 4.0)]
print(f"Total triangles in lights-trans near center button: {len(jewel_tris)}")
print(f"Jewel tris Z range: [{jewel_tris[:,:,2].min():.3f}, {jewel_tris[:,:,2].max():.3f}]")
