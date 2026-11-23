from PIL import Image

img = Image.open('test_renders/crop_abxy_white.png')
print('crop_abxy_white size:', img.size)

# Let's save a magnified version or inspect where the white pixels are
w, h = img.size
# Let's print out what colors are in the corners or regions of crop_abxy_white.png
import numpy as np
arr = np.array(img)
# Let's check min/max/mean in 4 quadrants
q1 = arr[:h//2, :w//2]
q2 = arr[:h//2, w//2:]
q3 = arr[h//2:, :w//2] # bottom left!
q4 = arr[h//2:, w//2:]

print('Top-Left mean:', q1.mean(axis=(0,1)))
print('Top-Right mean:', q2.mean(axis=(0,1)))
print('Bottom-Left mean:', q3.mean(axis=(0,1)))
print('Bottom-Right mean:', q4.mean(axis=(0,1)))

# Let's see what is in the bottom left!
print('Bottom-Left max:', q3.max(axis=(0,1)))
