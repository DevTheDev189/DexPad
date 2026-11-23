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

mesh12 = data['meshes'][12] # lights-trans
pos12 = get_buffer(mesh12['primitives'][0]['attributes']['POSITION'])
print(f"Mesh 12 (lights-trans): count={len(pos12)}")
print(f"   X: [{pos12[:,0].min():.3f}, {pos12[:,0].max():.3f}]")
print(f"   Y: [{pos12[:,1].min():.3f}, {pos12[:,1].max():.3f}]")
print(f"   Z: [{pos12[:,2].min():.3f}, {pos12[:,2].max():.3f}]")

# Check if there are other meshes around center (X ~ 0, Y ~ 3.5, Z ~ 1.5)
for i, m in enumerate(data['meshes']):
    name = m.get('name', '')
    pos = get_buffer(m['primitives'][0]['attributes']['POSITION'])
    near_center = pos[(np.abs(pos[:,0]) < 0.8) & (pos[:,1] > 3.0) & (pos[:,1] < 4.0) & (pos[:,2] > 0.8)]
    if len(near_center) > 0:
        print(f"Mesh {i} ({name}) has {len(near_center)} vertices near jewel area!")
