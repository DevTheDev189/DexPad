import json

with open("app/public/models/xbox_elite.glb", "rb") as f:
    f.seek(12)
    chunk_len = int.from_bytes(f.read(4), 'little')
    f.seek(20)
    gltf = json.loads(f.read(chunk_len).decode('utf-8'))

for i, node in enumerate(gltf['nodes']):
    mesh_idx = node.get('mesh')
    name = node.get('name')
    t = node.get('translation')
    r = node.get('rotation')
    s = node.get('scale')
    if mesh_idx is not None:
        mesh_name = gltf['meshes'][mesh_idx]['name']
        print(f"Node {i} '{name}': mesh={mesh_name}, trans={t}, rot={r}, scale={s}")
