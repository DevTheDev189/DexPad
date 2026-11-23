from PIL import Image
import numpy as np

img = Image.open('test_renders/crop_abxy_white.png')
arr = np.array(img)
print("crop_abxy_white shape:", arr.shape)

# Let's save a 4x magnified version and also draw where non-background pixels are
# What is the background color in crop_abxy_white?
# The faceplate is around [43, 30, 74]
# Let's find pixels that differ from faceplate!
faceplate = np.array([43, 30, 74])
diff = np.abs(arr[:,:,:3] - faceplate).sum(axis=2)
print("Points with large diff from faceplate (>40):", np.sum(diff > 40))

# Where are these points?
ys, xs = np.where(diff > 40)
if len(ys) > 0:
    print(f"X range: {xs.min()} - {xs.max()}")
    print(f"Y range: {ys.min()} - {ys.max()}")

# Let's print out what colors are found across the image
print("Min RGB in image:", arr[:,:,:3].min(axis=(0,1)))
print("Max RGB in image:", arr[:,:,:3].max(axis=(0,1)))
