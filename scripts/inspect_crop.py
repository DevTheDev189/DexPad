from PIL import Image

img = Image.open('test_renders/crop_abxy_white.png')
w, h = img.size
print('size:', w, h)

# Let's save a 4x magnified version and see the pixel values
img_scaled = img.resize((w*4, h*4), Image.Resampling.NEAREST)
img_scaled.save('test_renders/crop_abxy_magnified.png')

# Let's check the pixel values across the image:
# Where are the buttons in crop_abxy_white.png?
# The 4 buttons in ABXY diamond:
# Y is top
# X is left
# B is right
# A is bottom
# What is in the bottom left corner of each button or of the cluster?
print("Done magnifying.")
