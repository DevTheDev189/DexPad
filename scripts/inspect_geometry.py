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
    
    dtype_map = {
        5120: np.int8,
        5121: np.uint8,
        5122: np.int16,
        5123: np.uint16,
        5125: np.uint32,
        5126: np.float32,
    }
    dtype = dtype_map[ctype]
    
    num_components = {
        'SCALAR': 1,
        'VEC2': 2,
        'VEC3': 3,
        'VEC4': 4,
    }[type_]
    
    stride = bv.get('byteStride', dtype().itemsize * num_components)
    raw = bin_data[offset : offset + count * stride]
    if stride == dtype().itemsize * num_components:
        return np.frombuffer(raw, dtype=dtype).reshape(count, num_components)
    else:
        # non-standard stride
        res = []
        for i in range(count):
            item = np.frombuffer(raw[i*stride : i*stride + dtype().itemsize * num_components], dtype=dtype)
            res.append(item)
        return np.array(res)

for mesh_idx, mesh in enumerate(data['meshes']):
    name = mesh.get('name', 'unnamed')
    for prim in mesh['primitives']:
        pos_acc = prim['attributes']['POSITION']
        pos = get_buffer(pos_acc)
        min_v = pos.min(axis=0)
        max_v = pos.max(axis=0)
        print(f"Mesh {mesh_idx} ({name}): count={len(pos)}")
        print(f"   X: [{min_v[0]:.2f}, {max_v[0]:.2f}] Y: [{min_v[1]:.2f}, {max_v[1]:.2f}] Z: [{min_v[2]:.2f}, {max_v[2]:.2f}]")
