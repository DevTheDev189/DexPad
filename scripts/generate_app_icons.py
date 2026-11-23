import os
from PIL import Image, ImageDraw, ImageFilter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TAURI_ICONS_DIR = os.path.join(PROJECT_ROOT, "app", "src-tauri", "icons")
os.makedirs(TAURI_ICONS_DIR, exist_ok=True)

# 4x Supersampling canvas for pristine subpixel anti-aliasing
S = 2048
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

# 1. Background Squircle with Vertical Gradient (#182235 -> #0b111e)
grad = Image.new("RGBA", (S, S))
for y in range(S):
    t = y / (S - 1)
    r = int(24 + (11 - 24) * t)
    g = int(34 + (17 - 34) * t)
    b = int(53 + (30 - 53) * t)
    line = Image.new("RGBA", (S, 1), (r, g, b, 255))
    grad.paste(line, (0, y))

# Mask with Apple-style rounded rectangle (radius 24% of size)
mask = Image.new("L", (S, S), 0)
draw_mask = ImageDraw.Draw(mask)
margin = int(S * 0.02)
radius = int(S * 0.24)
draw_mask.rounded_rectangle([margin, margin, S - margin, S - margin], radius=radius, fill=255)

# Specular inner border
border_mask = Image.new("RGBA", (S, S), (0, 0, 0, 0))
draw_border = ImageDraw.Draw(border_mask)
draw_border.rounded_rectangle([margin, margin, S - margin, S - margin], radius=radius, outline=(255, 255, 255, 40), width=int(S * 0.015))

# Composite base tile
base_tile = Image.composite(grad, img, mask)
base_tile = Image.alpha_composite(base_tile, border_mask)

# 2. Cyan Capsule: Goes from Top-Left to Bottom-Right (\)
# Note: In Pillow, negative angle rotates CLOCKWISE!
cx, cy = S // 2, S // 2
capsule_w = int(S * 0.60)
capsule_h = int(S * 0.18)
capsule_r = capsule_h // 2

x0 = cx - capsule_w // 2
y0 = cy - capsule_h // 2

# Cyan gradient: #38bdf8 (56, 189, 248) -> #0284c7 (2, 132, 199)
cyan_grad_img = Image.new("RGBA", (capsule_w, capsule_h))
for x in range(capsule_w):
    t = x / (capsule_w - 1)
    r = int(56 + (2 - 56) * t)
    g = int(189 + (132 - 189) * t)
    b = int(248 + (199 - 248) * t)
    for y in range(capsule_h):
        cyan_grad_img.putpixel((x, y), (r, g, b, 255))

cyan_mask = Image.new("L", (capsule_w, capsule_h), 0)
ImageDraw.Draw(cyan_mask).rounded_rectangle([0, 0, capsule_w, capsule_h], radius=capsule_r, fill=255)
cyan_cutout = Image.new("RGBA", (capsule_w, capsule_h), (0, 0, 0, 0))
cyan_cutout.paste(cyan_grad_img, (0, 0), cyan_mask)

temp_cyan = Image.new("RGBA", (S, S), (0, 0, 0, 0))
temp_cyan.paste(cyan_cutout, (x0, y0), cyan_cutout)
# Rotate CLOCKWISE by 45 degrees: Pillow rotate(-45)
rot_cyan = temp_cyan.rotate(-45, resample=Image.Resampling.BICUBIC, center=(cx, cy))

# 3. Contoured White Stroke: Goes from Top-Right to Bottom-Left (/), shifted lower
# SVG path: M 65,21 C 69.4,25.4 69.4,32.6 65,37 L 57,45 L 45,57 L 37,65 C 32.6,69.4 25.4,69.4 21,65 C 16.6,60.6 16.6,53.4 21,49 L 29,41 Z
# with translate(0, 3)
def cubic_bezier(p0, p1, p2, p3, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        omt = 1 - t
        x = (omt**3)*p0[0] + 3*(omt**2)*t*p1[0] + 3*omt*(t**2)*p2[0] + (t**3)*p3[0]
        y = (omt**3)*p0[1] + 3*(omt**2)*t*p1[1] + 3*omt*(t**2)*p2[1] + (t**3)*p3[1]
        pts.append((x, y))
    return pts

svg_pts = []
svg_pts.extend(cubic_bezier((65, 21), (69.4, 25.4), (69.4, 32.6), (65, 37)))
svg_pts.append((57, 45))
svg_pts.append((45, 57))
svg_pts.append((37, 65))
svg_pts.extend(cubic_bezier((37, 65), (32.6, 69.4), (25.4, 69.4), (21, 65)))
svg_pts.extend(cubic_bezier((21, 65), (16.6, 60.6), (16.6, 53.4), (21, 49)))
svg_pts.append((29, 41))
svg_pts.append((65, 21))

# Scale to canvas S and apply +3% Y shift lower
scale = S / 100.0
shift_y = 3.0 * scale
scaled_pts = [(x * scale, (y + 3.0) * scale) for (x, y) in svg_pts]

# Layer B: White Stroke Mask
stroke_mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(stroke_mask).polygon(scaled_pts, fill=255)

# Drop shadow for white stroke
shadow_img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
shadow_mask = Image.new("L", (S, S), 0)
shadow_pts = [(x, y + int(S * 0.015)) for (x, y) in scaled_pts]
ImageDraw.Draw(shadow_mask).polygon(shadow_pts, fill=130)
shadow_img.paste(Image.new("RGBA", (S, S), (0, 0, 0, 130)), (0, 0), shadow_mask)
shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(int(S * 0.018)))

# Solid white cutout
white_img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
white_img.paste(Image.new("RGBA", (S, S), (248, 250, 252, 255)), (0, 0), stroke_mask)

# Composite all layers
final_glyph = Image.alpha_composite(rot_cyan, shadow_img)
final_glyph = Image.alpha_composite(final_glyph, white_img)

final_tile = Image.composite(final_glyph, Image.new("RGBA", (S, S), (0, 0, 0, 0)), mask)
master_img = Image.alpha_composite(base_tile, final_tile)

print("Master supersampled 2048 icon generated. Resampling target sizes...")

# 1. 512x512 icon.png
img_512 = master_img.resize((512, 512), Image.Resampling.LANCZOS)
img_512.save(os.path.join(TAURI_ICONS_DIR, "icon.png"), "PNG")
print("Saved icon.png (512x512)")

# 2. 256x256 128x128@2x.png
img_256 = master_img.resize((256, 256), Image.Resampling.LANCZOS)
img_256.save(os.path.join(TAURI_ICONS_DIR, "128x128@2x.png"), "PNG")
print("Saved 128x128@2x.png (256x256)")

# 3. 128x128 128x128.png
img_128 = master_img.resize((128, 128), Image.Resampling.LANCZOS)
img_128.save(os.path.join(TAURI_ICONS_DIR, "128x128.png"), "PNG")
print("Saved 128x128.png (128x128)")

# 4. 32x32 32x32.png
img_32 = master_img.resize((32, 32), Image.Resampling.LANCZOS)
img_32.save(os.path.join(TAURI_ICONS_DIR, "32x32.png"), "PNG")
img_32.save(os.path.join(PROJECT_ROOT, "app", "public", "32x32.png"), "PNG")
print("Saved 32x32.png (32x32)")

# 5. icon.ico (multi-resolution Windows ICO)
ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
master_img.save(os.path.join(TAURI_ICONS_DIR, "icon.ico"), format="ICO", sizes=ico_sizes)
print("Saved icon.ico (multi-resolution Windows executable)")

# 6. icon.icns (Apple ICNS)
try:
    master_img.save(os.path.join(TAURI_ICONS_DIR, "icon.icns"), format="ICNS")
    print("Saved icon.icns (Apple ICNS)")
except Exception as e:
    print(f"ICNS Note: {e}")

print("Successfully generated all DexPad app icons!")
