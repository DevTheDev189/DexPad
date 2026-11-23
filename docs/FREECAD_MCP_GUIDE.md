# FreeCAD MCP Integration & Modeling Guide
**Dexter Controller Project - RP2350 Pico 2 W Enclosure**

This guide documents how the FreeCAD Model Context Protocol (MCP) and XML-RPC bridge are configured in this workspace so that any incoming agent can immediately connect, inspect, and modify the 3D models.

---

## 1. System Architecture & Connection Details

* **FreeCAD Installation**: FreeCAD 1.1 on Windows (`C:\Program Files\FreeCAD 1.1\bin\freecad.exe` and `freecadcmd.exe`).
* **FreeCADMCP Addon**: Installed in `%APPDATA%\FreeCAD\v1-1\Mod\FreeCADMCP`.
* **Live GUI Server**:
  * FreeCAD runs an internal XML-RPC server listening on **`http://127.0.0.1:9875`**.
  * When FreeCAD is open on the user's desktop, Python scripts can execute code directly on the live GUI thread and update the active viewport in real time.
* **Execution Permissions**:
  * When running shell commands that touch FreeCAD or network ports on Windows, always use `BypassSandbox: true`.

---

## 2. How to Connect & Execute Code in FreeCAD

A dedicated helper script is provided at `scripts/mcp_freecad_exec.py`.

### A. Run a Python Script in the Live FreeCAD GUI
```powershell
python scripts/mcp_freecad_exec.py <script_path.py> [screenshot_output_path.png] [view_name]
```
* **Supported `view_name` options**: `"Isometric"`, `"Top"`, `"Front"`, `"Rear"`, `"Right"`, `"Left"`, `"Bottom"`.
* **Example**:
  ```powershell
  python scripts/mcp_freecad_exec.py scripts/run_goth_build.py case_3d/goth_isometric.png Isometric
  ```

### B. Inline Python Execution via XML-RPC
```python
import sys
sys.path.append(r"c:\Users\dwinslow\Documents\Dexter_Controller_Project\scripts")
import mcp_freecad_exec

code = """
import FreeCAD
doc = FreeCAD.activeDocument()
print("Active Document:", doc.Name)
print("Objects:", [o.Name for o in doc.Objects])
"""

mcp_freecad_exec.run_code(code, save_screenshot_path="case_3d/test_view.png", view_name="Isometric")
```

---

## 3. Project Files & Model Organization

Two separate models exist in this project to protect the clean base enclosure while developing the custom gift edition:

| File | Purpose | Script Generator |
| :--- | :--- | :--- |
| `case_3d/pico2w_enclosure.FCStd` | **Standard Base Case** (clean, unbranded for open-source GitHub release). | `scripts/generate_pico_case.py` |
| `case_3d/pico2w_enclosure-goth.FCStd` | **Gothic Imp Dexter Edition** (personalized gift edition with bat wings, "DEXTER", stitches, broken heart). | `scripts/generate_pico_case_goth.py` |

### Exported Manufacturing Files:
* **Gothic Edition STEP**: `case_3d/pico2w_case_bottom_goth.step`, `case_3d/pico2w_case_top_goth.step`
* **Gothic Edition STL**: `case_3d/pico2w_case_bottom_goth.stl`, `case_3d/pico2w_case_top_goth.stl`
* **Standard Edition STEP**: `case_3d/pico2w_case_bottom.step`, `case_3d/pico2w_case_top.step`
* **Standard Edition STL**: `case_3d/pico2w_case_bottom.stl`, `case_3d/pico2w_case_top.stl`

---

## 4. Parametric CAD Standards & Geometry Rules

1. **Outer Dimensions**:
   * Width: $24.9\text{ mm}$
   * Length: $54.9\text{ mm}$
   * Height: $8.6\text{ mm}$ (Symmetrical 50/50 parting split: $4.3\text{ mm}$ bottom / $4.3\text{ mm}$ top).
2. **PCB Cavity**:
   * Internal seat: $51.7 \times 21.7\text{ mm}$ ($0.35\text{ mm}$ clearance per side for Raspberry Pi Pico 2 W).
   * 4 Corner rest standoffs: $3.2 \times 3.2 \times 1.2\text{ mm}$ in bottom half.
3. **Cantilever Snap Clips (Must be Monolithically Rooted)**:
   * Tab length below parting line: **$2.4\text{ mm}$** (stops $0.4\text{ mm}$ above bottom floor).
   * Lead-in tip: Dual-tapered **$40^\circ$ triangular chisel point**.
   * Retention catch ledge: At $Z = -0.7\text{ mm}$ ($1.7\text{ mm}$ from tip) locking into $2.7–3.7\text{ mm}$ slots in bottom wall.
   * **Root Anchor**: Cantilever arms extend upward to $Z = 3.5\text{ mm}$, fusing directly into the solid roof ceiling ($Z = 2.8\text{ mm}$) and sidewalls. `len(shape.Solids)` must always equal 1 (zero floating bodies).
4. **Authentic Trapezoidal Micro-USB Cutout**:
   * Symmetrical split along parting plane ($Z = 4.3\text{ mm}$).
   * Lofted wire: $8.0\text{ mm}$ top flat, vertical flanks, $45^\circ$ bottom chamfers ($6.2\text{ mm}$ base), and an outer $10.8 \times 5.0\text{ mm}$ lead-in funnel bevel.
5. **Camera-Style Dual Holes**:
   * Status LED ($X = 6.74, Y = 48.14$) and BOOTSEL ($X = 8.95, Y = 40.95$).
   * Cut using smooth S-curve revolved profiles forming concave spherical dishes with tangent rounded lips.
   * Concentric $0.15\text{ mm}$ debossed halo accent rings encircle both wells.
6. **Flank Grip Flutes**:
   * 5 linear grooves ($1.2\text{ mm}$ wide, $0.45\text{ mm}$ deep) on left and right outer walls.
   * Cut continuously across the parting line from $Z = 1.2\text{ mm}$ (bottom fillet tangent) to $Z = 7.4\text{ mm}$ (top fillet tangent) to conceal the seam when assembled.

---

## 5. Gothic Imp Edition Motifs (PlayVital Style)

* **Bat-Wing Crest**: Centered at $(12.45, 31.5)$, width $12.5\text{ mm}$, height $5.2\text{ mm}$, debossed $0.22\text{ mm}$.
* **"DEXTER" Typography**: Centered at $(12.45, 24.0)$, height $2.3\text{ mm}$, debossed $0.22\text{ mm}$.
* **Frankenstein Stitched Scar**: Diagonal cut from $(13.8, 9.5)$ to $(19.8, 16.5)$ with 4 cross-stitches.
* **Broken Heart Motif**: Centered at $(7.5, 13.0)$, size $5.2\text{ mm}$ with zigzag crack.
* **Recommended Material & Finish**: SLA 9600 Resin with Matte Sky Blue spray paint.

---

## 6. General Coding Rules for Agents

* **No Emojis**: Strictly zero emojis in code, docstrings, commits, agent prose, and UI text.
* **File Links**: Always use clickable markdown links with `file:///` format and forward slashes.
* **STEP Export Method**: Always use `shape.exportStep(path)` rather than `Part.export([shape], path)` to ensure NURBS surface topology is fully written.
