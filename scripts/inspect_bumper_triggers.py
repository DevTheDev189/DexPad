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

print("Bumpers mesh analysis:")
print(f"X range: [{pos6[:,0].min():.3f}, {pos6[:,0].max():.3f}]")
print(f"Triangles with |X| < 1.0 (center bridge): {np.sum(np.abs(t6_c[:, 0]) < 1.0)}")
print(f"Triangles with X < -1.0 (left bumper): {np.sum(t6_c[:, 0] < -1.0)}")
print(f"Triangles with X > 1.0 (right bumper): {np.sum(t6_c[:, 0] > 1.0)}")

# Check triggers mesh analysis
pos4 = get_buffer(data['meshes'][4]['primitives'][0]['attributes']['POSITION'])
indices4 = get_buffer(data['meshes'][4]['primitives'][0]['indices']).flatten()
t4 = pos4[indices4].reshape(-1, 3, 3)
t4_c = t4.mean(axis=1)

print("\nTriggers mesh analysis:")
print(f"X range: [{pos4[:,0].min():.3f}, {pos4[:,0].max():.3f}]")
print(f"Triangles with |X| < 1.0 (center): {np.sum(np.abs(t4_c[:, 0]) < 1.0)}")
print(f"Triangles with X < -1.0 (left trigger): {np.sum(t4_c[:, 0] < -1.0)}")
print(f"Triangles with X > 1.0 (right trigger): {np.sum(t4_c[:, 0] > 1.0)}")
print(f"Left trigger X span: [{pos4[pos4[:,0] < 0, 0].min():.3f}, {pos4[pos4[:,0] < 0, 0].max():.3f}]")
print(f"Right trigger X span: [{pos4[pos4[:,0] > 0, 0].min():.3f}, {pos4[pos4[:,0] > 0, 0].max():.3f}]")
