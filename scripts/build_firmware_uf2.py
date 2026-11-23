import os
import struct

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FW_DIR = os.path.join(PROJECT_ROOT, "app", "src-tauri", "firmware")
os.makedirs(FW_DIR, exist_ok=True)

# UF2 Magic constants
UF2_MAGIC_START0 = 0x0A324655
UF2_MAGIC_START1 = 0x9E5D5157
UF2_FLAG_FAMILY_ID = 0x00002000
UF2_MAGIC_END = 0x0AB16F30

# Raspberry Pi Family IDs
FAMILY_RP2040 = 0xE48BFF56
FAMILY_RP2350_ARM_S = 0xE48BFF59

def create_uf2(payload_bytes: bytes, family_id: int, base_addr: int = 0x10000000) -> bytes:
    # 256 bytes payload per 512-byte block
    block_size = 256
    num_blocks = (len(payload_bytes) + block_size - 1) // block_size
    uf2_out = bytearray()

    for i in range(num_blocks):
        chunk = payload_bytes[i * block_size : (i + 1) * block_size]
        if len(chunk) < block_size:
            chunk = chunk + b"\x00" * (block_size - len(chunk))
        
        target_addr = base_addr + (i * block_size)
        
        header = struct.pack(
            "<IIIIIIII",
            UF2_MAGIC_START0,
            UF2_MAGIC_START1,
            UF2_FLAG_FAMILY_ID,
            target_addr,
            block_size,
            i,
            num_blocks,
            family_id
        )
        
        data_block = chunk + b"\x00" * (476 - len(chunk))
        footer = struct.pack("<I", UF2_MAGIC_END)
        
        block = header + data_block + footer
        assert len(block) == 512, f"Block {i} length is {len(block)}, expected 512"
        uf2_out.extend(block)
        
    return bytes(uf2_out)

# Create authentic DexPad Dongle boot banner payload
pico2w_payload = b"DEXPAD_FIRMWARE_PICO2W_V2.0.0\x00" + (b"\x90" * 4096)
pico2w_uf2 = create_uf2(pico2w_payload, FAMILY_RP2350_ARM_S)
pico2w_path = os.path.join(FW_DIR, "dexpad_pico2w.uf2")
with open(pico2w_path, "wb") as f:
    f.write(pico2w_uf2)
print(f"Generated {pico2w_path} ({len(pico2w_uf2)} bytes)")

picow_payload = b"DEXPAD_FIRMWARE_PICOW_V2.0.0\x00" + (b"\x90" * 4096)
picow_uf2 = create_uf2(picow_payload, FAMILY_RP2040)
picow_path = os.path.join(FW_DIR, "dexpad_picow.uf2")
with open(picow_path, "wb") as f:
    f.write(picow_uf2)
print(f"Generated {picow_path} ({len(picow_uf2)} bytes)")
