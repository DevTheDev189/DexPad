import struct
import json

with open("app/public/models/xbox_elite.glb", "rb") as f:
    f.seek(12)
    chunk_length, chunk_type = struct.unpack("<I4s", f.read(8))
    json_bytes = f.read(chunk_length)
    gltf = json.loads(json_bytes.decode("utf-8"))

print("Textures count:", len(gltf.get("textures", [])))
print("Images count:", len(gltf.get("images", [])))
for i, m in enumerate(gltf.get("materials", [])):
    print(f"Mat {i}: {m.get('name')}, pbr: {m.get('pbrMetallicRoughness')}")
for i, mesh in enumerate(gltf.get("meshes", [])):
    print(f"Mesh {i}: {mesh.get('name')}")
    for p in mesh.get("primitives", []):
        print(f"   mat: {p.get('material')}, attrs: {list(p.get('attributes', {}).keys())}")
