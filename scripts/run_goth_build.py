import sys
import os

# Add scripts directory to path
scripts_dir = r"c:\Users\dwinslow\Documents\Dexter_Controller_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import generate_pico_case_goth
import importlib
importlib.reload(generate_pico_case_goth)

doc = generate_pico_case_goth.create_goth_enclosure()

import FreeCADGui
FreeCADGui.Selection.clearSelection()
FreeCADGui.activeDocument().activeView().viewIsometric()
FreeCADGui.activeDocument().activeView().fitAll()
print("FreeCAD view updated to Isometric!")
