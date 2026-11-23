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

# Check how we can distinguish base vs letter triangles:
# A: center ~ (3.93, 1.7)
# Base triangles (Comp 1): Y spans [1.15, 2.17], radius from center (3.92, 1.71)
# Notice: Base triangles form a cylinder with radius ~ 0.51
# Letter A triangles are clustered tightly around the center with radius < 0.32!
# Let's check the radius from button center for base vs letter:
for btn, cx, cy in [('A', 3.92, 1.71), ('B', 4.99, 2.62), ('X', 2.88, 2.73), ('Y', 3.95, 3.68)]:
    # filter tris belonging to this button
    dx = t10_c[:, 0] - cx
    dy = t10_c[:, 1] - cy
    dist = np.sqrt(dx**2 + dy**2)
    btn_tris = np.where(dist < 0.65)[0]
    
    # In btn_tris, find normal or triangle size or connected components
    print(f"Button {btn}: {len(btn_tris)} triangles total.")
