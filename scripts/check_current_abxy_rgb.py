from PIL import Image
import numpy as np

img = Image.open('test_renders/crop_abxy_white.png')
arr = np.array(img)
print("crop_abxy_white shape:", arr.shape)
# Save 4x nearest
img.resize((img.width * 4, img.height * 4), Image.Resampling.NEAREST).save('test_renders/crop_abxy_current_large.png')

# Let's find all pixels with pure or near-pure black (base) and white (letters)
# Base color was set to 0x060609. In render with lights, what is base RGB?
# Let's sample the 4 button centers:
# Let's find coordinates of dark button caps:
dark_mask = (arr[:,:,0] < 25) & (arr[:,:,1] < 25) & (arr[:,:,2] < 35)
print("Dark button pixels (<25, <25, <35) count:", np.sum(dark_mask))

# Let's find bright pixels (>180)
bright_mask = (arr[:,:,0] > 180) & (arr[:,:,1] > 180) & (arr[:,:,2] > 180)
print("Bright letter pixels (>180) count:", np.sum(bright_mask))

ys, xs = np.where(bright_mask)
for i in range(min(5, len(ys))):
    print(f"Bright pixel at x={xs[i]}, y={ys[i]}: RGB={arr[ys[i], xs[i]]}")
