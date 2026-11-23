import sys
import xmlrpc.client
import base64

def run_code(code_str, save_screenshot_path=None, view_name="Isometric"):
    server = xmlrpc.client.ServerProxy("http://127.0.0.1:9875")
    res = server.execute_code(code_str)
    print("Full result:", res)
        
    if save_screenshot_path:
        try:
            shot = server.get_active_screenshot(view_name)
            if isinstance(shot, str):
                data = base64.b64decode(shot)
                with open(save_screenshot_path, "wb") as f:
                    f.write(data)
                print(f"Saved screenshot to {save_screenshot_path}")
            elif isinstance(shot, dict) and shot.get("success") and "image" in shot:
                data = base64.b64decode(shot["image"])
                with open(save_screenshot_path, "wb") as f:
                    f.write(data)
                print(f"Saved screenshot to {save_screenshot_path}")
        except Exception as e:
            print("Screenshot error:", e)
    return res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            code = f.read()
        shot_path = sys.argv[2] if len(sys.argv) > 2 else None
        view = sys.argv[3] if len(sys.argv) > 3 else "Isometric"
        run_code(code, shot_path, view)
    else:
        run_code("import FreeCAD; print('Active doc:', FreeCAD.activeDocument().Name if FreeCAD.activeDocument() else None)")
