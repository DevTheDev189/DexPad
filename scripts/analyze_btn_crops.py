from PIL import Image
import numpy as np

for name in ['btn_a', 'btn_b', 'btn_x', 'btn_y']:
    img = Image.open(f'test_renders/{name}_large.png')
    arr = np.array(img)
    # Check max and mean
    print(f"=== {name} ===")
    print("Shape:", arr.shape)
    # Find brightest pixels
    bright = arr > 180
    print("Count of bright pixels (>180):", np.sum(bright) // 3)
    # Find where bright pixels are located in the (280, 280) image
    y_coords, x_coords = np.where(arr[:,:,0] > 180)
    if len(y_coords) > 0:
        print(f"Bright pixels Y range: {y_coords.min()}-{y_coords.max()} (height {arr.shape[0]})")
        print(f"Bright pixels X range: {x_coords.min()}-{x_coords.max()} (width {arr.shape[1]})")
        print(f"Bright center: Y={y_coords.mean():.1f}, X={x_coords.mean():.1f}")
