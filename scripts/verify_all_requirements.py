from PIL import Image
import numpy as np

# 1. Inspect ABXY buttons crop
img_abxy = Image.open('test_renders/crop_abxy_white.png')
arr_abxy = np.array(img_abxy)
print(f"crop_abxy_white: shape={arr_abxy.shape}, min={arr_abxy.min(axis=(0,1))[:3]}, max={arr_abxy.max(axis=(0,1))[:3]}, mean={arr_abxy.mean(axis=(0,1))[:3]}")

# 2. Check each button (A, B, X, Y)
# Button A is bottom (x: 50-110, y: 110-170)
# Button B is right (x: 95-155, y: 55-115)
# Button X is left (x: 10-70, y: 55-115)
# Button Y is top (x: 50-110, y: 10-70)

for btn, (x1, y1, x2, y2) in [
    ('Button Y', (50, 10, 110, 70)),
    ('Button X', (10, 55, 70, 115)),
    ('Button B', (95, 55, 155, 115)),
    ('Button A', (50, 110, 110, 170)),
]:
    box = arr_abxy[y1:y2, x1:x2]
    # Check bottom left of button
    bh, bw = box.shape[:2]
    bl = box[bh*2//3:, :bw//3]
    # Count of white pixels (>180) in entire button
    white_px = np.sum(np.all(box[:,:,:3] > 180, axis=2))
    # Count of deep black base pixels (<20) in button
    black_px = np.sum(np.all(box[:,:,:3] < 20, axis=2))
    print(f"{btn}: white_pixels={white_px}, black_pixels={black_px}, BL_max={bl.max(axis=(0,1))[:3]}, BL_mean={bl.mean(axis=(0,1))[:3]}")

# 3. Inspect Button A selected vs idle:
img_idle = Image.open('test_renders/galaxy_front_overview_crop.png')
img_sel = Image.open('test_renders/galaxy_button_a_selected_crop.png')
arr_idle = np.array(img_idle)
arr_sel = np.array(img_sel)

diff = np.abs(arr_sel.astype(int) - arr_idle.astype(int))
print(f"Diff between Button A selected and idle: max diff={diff.max()}, total changed px={np.sum(diff.max(axis=2) > 10)}")

# 4. Check Home button selected vs idle:
img_home = Image.open('test_renders/galaxy_home_selected_crop.png')
arr_home = np.array(img_home)
diff_home = np.abs(arr_home.astype(int) - arr_idle.astype(int))
print(f"Diff between Home selected and idle: max diff={diff_home.max()}, total changed px={np.sum(diff_home.max(axis=2) > 10)}")

# 5. Check bottom area of galaxy_front_overview_crop for floor shadow:
# Floor used to be at y: 650-760
floor_area = arr_idle[650:750, 200:500]
print(f"Floor area (y=650..750) mean RGB={floor_area.mean(axis=(0,1))[:3]}")
