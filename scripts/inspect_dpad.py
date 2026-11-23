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

mesh19 = data['meshes'][19] # d-pad-faceted
pos19 = get_buffer(mesh19['primitives'][0]['attributes']['POSITION'])
min19 = pos19.min(axis=0)
max19 = pos19.max(axis=0)
center19 = (min19 + max19) / 2.0
print(f"Mesh 19 (faceted) center: {center19}, range X: [{min19[0]:.2f}, {max19[0]:.2f}], Y: [{min19[1]:.2f}, {max19[1]:.2f}], Z: [{min19[2]:.2f}, {max19[2]:.2f}]")

mesh20 = data['meshes'][20] # d-pad-cross
pos20 = get_buffer(mesh20['primitives'][0]['attributes']['POSITION'])
min20 = pos20.min(axis=0)
max20 = pos20.max(axis=0)
center20 = (min20 + max20) / 2.0
print(f"Mesh 20 (cross) center: {center20}, range X: [{min20[0]:.2f}, {max20[0]:.2f}], Y: [{min20[1]:.2f}, {max20[1]:.2f}], Z: [{min20[2]:.2f}, {max20[2]:.2f}]")
