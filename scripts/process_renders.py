import os
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

def clean_extract_controller(input_path, output_path, crop_box, padding=16):
    img = Image.open(input_path).convert('RGBA')
    w, h = img.size
    rgb = np.array(img.convert('RGB'), dtype=np.float32)
    
    bg_color = np.array([247, 247, 247], dtype=np.float32)
    diff = np.sqrt(np.sum((rgb - bg_color) ** 2, axis=2))
    
    # 255 for background candidates
    bg_candidate = (diff < 15.0).astype(np.uint8) * 255
    mask_img = Image.fromarray(bg_candidate, mode='L')
    
    # Flood-fill from corners
    ImageDraw.floodfill(mask_img, (0, 0), 128)
    ImageDraw.floodfill(mask_img, (w - 1, 0), 128)
    ImageDraw.floodfill(mask_img, (0, h - 1), 128)
    ImageDraw.floodfill(mask_img, (w - 1, h - 1), 128)
    
    mask_arr = np.array(mask_img)
    is_outer_bg = (mask_arr == 128)
    
    alpha = np.ones((h, w), dtype=np.uint8) * 255
    alpha[is_outer_bg] = 0
    alpha_img = Image.fromarray(alpha, mode='L').filter(ImageFilter.GaussianBlur(0.75))
    img.putalpha(alpha_img)
    
    # Apply tight crop
    x0, y0, x1, y1 = crop_box
    crop_rect = (
        max(0, x0 - padding),
        max(0, y0 - padding),
        min(w, x1 + padding),
        min(h, y1 + padding)
    )
    cropped = img.crop(crop_rect)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cropped.save(output_path, 'PNG')
    print(f"Extracted {output_path}: size={cropped.size}")
    return cropped.size, crop_rect

if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    front_raw = os.path.join(root_dir, 'steelseries-nimbus-wireless-gaming-controller-apple-white-3d-model-61b29ae687.webp')
    top_raw = os.path.join(root_dir, 'steelseries-nimbus-wireless-gaming-controller-apple-white-3d-model-9908df8abd.webp')
    
    front_out = os.path.join(root_dir, 'app', 'src', 'assets', 'controller_front.png')
    top_out = os.path.join(root_dir, 'app', 'src', 'assets', 'controller_top.png')
    
    front_size, front_rect = clean_extract_controller(front_raw, front_out, (410, 141, 1067, 662), padding=16)
    top_size, top_rect = clean_extract_controller(top_raw, top_out, (146, 128, 1336, 684), padding=16)
    
    # Calculate relative button hotspots for front view
    # Raw coordinates -> Offset by front_rect[0], front_rect[1] -> Percentages
    fx0, fy0 = front_rect[0], front_rect[1]
    fw, fh = front_size
    
    raw_front_points = {
        'a': (531.6 + 408 - 20, 191.4 + 140 - 20),
        'b': (580.2 + 408 - 20, 137.8 + 140 - 20),
        'x': (483.0 + 408 - 20, 142.7 + 140 - 20),
        'y': (531.7 + 408 - 20, 91.2 + 140 - 20),
        'menu': (350.0 + 408 - 20, 183.5 + 140 - 20),
        'dpad_up': (168.7 + 408 - 20, 107.9 + 140 - 20),
        'dpad_down': (168.7 + 408 - 20, 177.9 + 140 - 20),
        'dpad_left': (133.7 + 408 - 20, 142.9 + 140 - 20),
        'dpad_right': (203.7 + 408 - 20, 142.9 + 140 - 20),
        'left_stick': (247.8 + 408 - 20, 276.3 + 140 - 20),
        'right_stick': (453.5 + 408 - 20, 276.3 + 140 - 20),
    }
    
    print("\n--- FRONT VIEW HOTSPOTS (Percentage X%, Y%) ---")
    for k, (rx, ry) in raw_front_points.items():
        px = round(((rx - fx0) / fw) * 100, 2)
        py = round(((ry - fy0) / fh) * 100, 2)
        print(f"'{k}': {{ x: {px}, y: {py} }},")
