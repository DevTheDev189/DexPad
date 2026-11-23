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

pos10 = get_buffer(data['meshes'][10]['primitives'][0]['attributes']['POSITION'])
indices10 = get_buffer(data['meshes'][10]['primitives'][0]['indices']).flatten()

t10 = pos10[indices10].reshape(-1, 3, 3)
t10_c = t10.mean(axis=1)

# Test thresholding
a_base = np.where((t10_c[:, 1] < 2.0) & (t10_c[:, 2] <= 1.65))[0]
a_letter = np.where((t10_c[:, 1] < 2.0) & (t10_c[:, 2] > 1.65))[0]
print(f"Button A -> Base: {len(a_base)} tris, Letter: {len(a_letter)} tris. Total: {len(a_base)+len(a_letter)}")

b_base = np.where((t10_c[:, 0] >= 3.9) & (t10_c[:, 1] >= 2.0) & (t10_c[:, 1] <= 3.2) & (t10_c[:, 2] <= 1.20))[0]
b_letter = np.where((t10_c[:, 0] >= 3.9) & (t10_c[:, 1] >= 2.0) & (t10_c[:, 1] <= 3.2) & (t10_c[:, 2] > 1.20))[0]
print(f"Button B -> Base: {len(b_base)} tris, Letter: {len(b_letter)} tris. Total: {len(b_base)+len(b_letter)}")

x_base = np.where((t10_c[:, 0] < 3.9) & (t10_c[:, 1] >= 2.0) & (t10_c[:, 1] <= 3.2) & (t10_c[:, 2] <= 1.47))[0]
x_letter = np.where((t10_c[:, 0] < 3.9) & (t10_c[:, 1] >= 2.0) & (t10_c[:, 1] <= 3.2) & (t10_c[:, 2] > 1.47))[0]
print(f"Button X -> Base: {len(x_base)} tris, Letter: {len(x_letter)} tris. Total: {len(x_base)+len(x_letter)}")

y_base = np.where((t10_c[:, 1] > 3.2) & (t10_c[:, 2] <= 1.05))[0]
y_letter = np.where((t10_c[:, 1] > 3.2) & (t10_c[:, 2] > 1.05))[0]
print(f"Button Y -> Base: {len(y_base)} tris, Letter: {len(y_letter)} tris. Total: {len(y_base)+len(y_letter)}")
