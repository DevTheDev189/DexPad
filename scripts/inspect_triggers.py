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

mesh4 = data['meshes'][4] # triggers
pos4 = get_buffer(mesh4['primitives'][0]['attributes']['POSITION'])
indices4 = get_buffer(mesh4['primitives'][0]['indices']).flatten()

t4 = pos4[indices4].reshape(-1, 3, 3)
t4_c = t4.mean(axis=1)

print(f"Total vertices in triggers: {len(pos4)}")
print(f"Total triangles in triggers: {len(t4)}")
print(f"X range: [{pos4[:,0].min():.3f}, {pos4[:,0].max():.3f}]")
print(f"Y range: [{pos4[:,1].min():.3f}, {pos4[:,1].max():.3f}]")
print(f"Z range: [{pos4[:,2].min():.3f}, {pos4[:,2].max():.3f}]")

# Now let's inspect Mesh 6 (bumpers-trans):
mesh6 = data['meshes'][6] # bumpers-trans
pos6 = get_buffer(mesh6['primitives'][0]['attributes']['POSITION'])
print(f"\nTotal vertices in bumpers: {len(pos6)}")
print(f"Bumpers X range: [{pos6[:,0].min():.3f}, {pos6[:,0].max():.3f}]")
print(f"Bumpers Y range: [{pos6[:,1].min():.3f}, {pos6[:,1].max():.3f}]")
print(f"Bumpers Z range: [{pos6[:,2].min():.3f}, {pos6[:,2].max():.3f}]")

# What parts of triggers are exposed vs inside the controller?
# Check Z distribution:
print("\nTrigger triangle count by Z depth:")
print("Z < -2.0:", np.sum(t4_c[:, 2] < -2.0))
print("-2.0 <= Z < -1.0:", np.sum((t4_c[:, 2] >= -2.0) & (t4_c[:, 2] < -1.0)))
print("-1.0 <= Z < 0.0:", np.sum((t4_c[:, 2] >= -1.0) & (t4_c[:, 2] < 0.0)))
print("Z >= 0.0:", np.sum(t4_c[:, 2] >= 0.0))
