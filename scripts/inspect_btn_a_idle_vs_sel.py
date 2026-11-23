from PIL import Image
import numpy as np

img_idle = Image.open('test_renders/galaxy_front_overview_crop.png')
img_home = Image.open('test_renders/galaxy_home_selected_crop.png')
arr_idle = np.array(img_idle)
arr_home = np.array(img_home)

diff = np.abs(arr_home.astype(int) - arr_idle.astype(int))
# Where did pixels change?
ys, xs = np.where(diff.max(axis=2) > 40)
print(f"Pixels changed count: {len(ys)}")
print(f"X range: {xs.min()} - {xs.max()}")
print(f"Y range: {ys.min()} - {ys.max()}")

# Button A is around x=480..550, y=380..450
btn_a_mask = (xs >= 460) & (xs <= 560) & (ys >= 360) & (ys <= 460)
print(f"Button A changed pixels: {np.sum(btn_a_mask)}")

# Home jewel is around x=320..380, y=260..320
home_mask = (xs >= 300) & (xs <= 400) & (ys >= 240) & (ys <= 340)
print(f"Home jewel changed pixels: {np.sum(home_mask)}")

# Let's save a crop of Button A in idle (selected) vs in home (unselected)
# In galaxy_front_overview, Button A was SELECTED (glowing with galaxy texture!)
# In galaxy_home_selected, Button A was UNSELECTED (idle jet black!)
crop_a_selected = img_idle.crop((460, 360, 560, 460))
crop_a_unselected = img_home.crop((460, 360, 560, 460))
crop_a_selected.save('test_renders/crop_btn_a_selected.png')
crop_a_unselected.save('test_renders/crop_btn_a_unselected_jetblack.png')

print("Saved crop_btn_a_selected.png and crop_btn_a_unselected_jetblack.png!")
