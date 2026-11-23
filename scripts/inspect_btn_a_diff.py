from PIL import Image
import numpy as np

img_idle = Image.open('test_renders/galaxy_front_overview_crop.png')
img_sel = Image.open('test_renders/galaxy_button_a_selected_crop.png')
arr_idle = np.array(img_idle)
arr_sel = np.array(img_sel)

diff = np.abs(arr_sel.astype(int) - arr_idle.astype(int))
print("Diff max:", diff.max())
print("Total changed pixels (>5):", np.sum(diff.max(axis=2) > 5))
ys, xs = np.where(diff.max(axis=2) > 5)
if len(ys) > 0:
    print(f"Changed pixels X range: {xs.min()} - {xs.max()}, Y range: {ys.min()} - {ys.max()}")
    print("Mean RGB in idle at changed pixels:", arr_idle[ys, xs].mean(axis=0))
    print("Mean RGB in sel at changed pixels:", arr_sel[ys, xs].mean(axis=0))
else:
    print("NO CHANGED PIXELS!")
