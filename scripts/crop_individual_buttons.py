from PIL import Image

full = Image.open('test_renders/galaxy_front_overview_crop.png')
print('galaxy_front_overview_crop size:', full.size)

# The ABXY button cluster in galaxy_front_overview_crop is around x=440-600, y=280-470
# Let's save 4 individual crops for buttons A, B, X, Y
# In full coordinates:
# A is around x=490-550, y=380-445
# B is around x=535-595, y=330-395
# X is around x=445-505, y=330-395
# Y is around x=490-550, y=285-350

crops = {
    'btn_a': (485, 380, 555, 450),
    'btn_b': (535, 330, 605, 400),
    'btn_x': (440, 330, 510, 400),
    'btn_y': (485, 280, 555, 350),
}

for name, box in crops.items():
    c = full.crop(box)
    c.resize((280, 280), Image.Resampling.NEAREST).save(f'test_renders/{name}_large.png')
    print(f'Saved {name}_large.png')
