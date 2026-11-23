from PIL import Image
import numpy as np

img = Image.open('test_renders/crop_abxy_white.png')
arr = np.array(img)

# Find coordinates of non-background pixels:
# Background is dark purple: around [30, 20, 50]
# Let's inspect 4 boxes for the 4 buttons:
# Button Y: top (x: 60-100, y: 15-55)
# Button X: left (x: 20-60, y: 65-105)
# Button B: right (x: 100-140, y: 65-105)
# Button A: bottom (x: 60-100, y: 115-155)

for name, (x1, y1, x2, y2) in [
    ('Button Y', (60, 15, 100, 55)),
    ('Button X', (20, 65, 60, 105)),
    ('Button B', (100, 65, 140, 105)),
    ('Button A', (60, 115, 100, 155)),
]:
    box = arr[y1:y2, x1:x2]
    # Check bottom-left of each button!
    bw = x2 - x1
    bh = y2 - y1
    bl = box[bh*2//3:, :bw//3]
    print(f"{name}: center mean={box[bh//4:bh*3//4, bw//4:bw*3//4].mean(axis=(0,1))[:3]}")
    print(f"   bottom-left region: min={bl.min(axis=(0,1))[:3]}, max={bl.max(axis=(0,1))[:3]}, mean={bl.mean(axis=(0,1))[:3]}")
