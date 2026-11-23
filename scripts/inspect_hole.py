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

# Look at Mesh 12 (lights-trans):
pos12 = get_buffer(data['meshes'][12]['primitives'][0]['attributes']['POSITION'])
indices12 = get_buffer(data['meshes'][12]['primitives'][0]['indices']).flatten()

print(f"Total indices in lights-trans: {len(indices12)}")

# And look at Mesh 0 (body-top-case) near jewel:
pos0 = get_buffer(data['meshes'][0]['primitives'][0]['attributes']['POSITION'])
indices0 = get_buffer(data['meshes'][0]['primitives'][0]['indices']).flatten()
t0 = pos0[indices0].reshape(-1, 3, 3)
t0_c = t0.mean(axis=1)
near_hole = t0[(np.abs(t0_c[:,0]) < 0.8) & (t0_c[:,1] > 3.4) & (t0_c[:,1] < 4.2)]
print("Hole boundary on body-top-case: triangles=", len(near_hole))
print(f"Hole X: [{near_hole[:,:,0].min():.3f}, {near_hole[:,:,0].max():.3f}]")
print(f"Hole Y: [{near_hole[:,:,1].min():.3f}, {near_hole[:,:,1].max():.3f}]")
print(f"Hole Z: [{near_hole[:,:,2].min():.3f}, {near_hole[:,:,2].max():.3f}]")
