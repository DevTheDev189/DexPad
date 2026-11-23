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

for i, m in enumerate(data['meshes']):
    name = m.get('name', '')
    pos = get_buffer(m['primitives'][0]['attributes']['POSITION'])
    near = pos[(np.abs(pos[:,0]) < 0.6) & (pos[:,1] >= 3.4) & (pos[:,1] <= 4.2) & (pos[:,2] >= 0.5)]
    if len(near) > 0:
        print(f"Mesh {i} ({name}): {len(near)} vertices. X: [{near[:,0].min():.2f}, {near[:,0].max():.2f}], Y: [{near[:,1].min():.2f}, {near[:,1].max():.2f}], Z: [{near[:,2].min():.2f}, {near[:,2].max():.2f}]")
