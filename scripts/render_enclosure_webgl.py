import os
import struct
import base64
from playwright.sync_api import sync_playwright
from PIL import Image

WORKSPACE_DIR = r"c:\Users\dwinslow\Documents\Dexter_Controller_Project"
BOTTOM_STL = os.path.join(WORKSPACE_DIR, "case_3d", "pico2w_case_bottom.stl")
TOP_STL = os.path.join(WORKSPACE_DIR, "case_3d", "pico2w_case_top.stl")
OUT_PNG = os.path.join(WORKSPACE_DIR, "docs", "dexpad_case_render.png")
HTML_PATH = os.path.join(WORKSPACE_DIR, "scripts", "render_enclosure_temp.html")
THREE_JS = os.path.join(WORKSPACE_DIR, "scripts", "three.min.js")

def parse_stl(filename):
    with open(filename, "rb") as f:
        f.read(80) # skip header
        num_tris = struct.unpack("<I", f.read(4))[0]
        positions = []
        normals = []
        for _ in range(num_tris):
            data = f.read(50)
            nx, ny, nz = struct.unpack("<3f", data[0:12])
            v1 = struct.unpack("<3f", data[12:24])
            v2 = struct.unpack("<3f", data[24:36])
            v3 = struct.unpack("<3f", data[36:48])
            
            if abs(nx) < 1e-5 and abs(ny) < 1e-5 and abs(nz) < 1e-5:
                ax, ay, az = v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2]
                bx, by, bz = v3[0]-v1[0], v3[1]-v1[1], v3[2]-v1[2]
                cx = ay*bz - az*by
                cy = az*bx - ax*bz
                cz = ax*by - ay*bx
                l = (cx*cx + cy*cy + cz*cz)**0.5
                if l > 1e-6:
                    nx, ny, nz = cx/l, cy/l, cz/l
            
            for v in (v1, v2, v3):
                positions.extend(v)
                normals.extend([nx, ny, nz])
                
    pos_bytes = struct.pack(f"<{len(positions)}f", *positions)
    norm_bytes = struct.pack(f"<{len(normals)}f", *normals)
    return base64.b64encode(pos_bytes).decode("ascii"), base64.b64encode(norm_bytes).decode("ascii"), num_tris

def generate_html():
    print("Reading and parsing STL files...")
    b_pos, b_norm, b_tris = parse_stl(BOTTOM_STL)
    t_pos, t_norm, t_tris = parse_stl(TOP_STL)
    print(f"Bottom STL: {b_tris} tris, Top STL: {t_tris} tris")
    
    with open(THREE_JS, "r", encoding="utf-8") as f:
        three_js_code = f.read()

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DexPad Enclosure Studio Render</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: radial-gradient(ellipse at 50% 35%, #182232 0%, #0d131e 50%, #06080e 100%);
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        #canvas {{
            width: 100%;
            height: 100%;
            display: block;
        }}
        .header {{
            position: absolute;
            top: 36px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            pointer-events: none;
            z-index: 10;
        }}
        .header h1 {{
            color: #f1f5f9;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 6px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.8);
        }}
        .header p {{
            color: #64748b;
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.2px;
        }}
        .header p span {{
            color: #38bdf8;
            font-weight: 600;
        }}
        .overlay {{
            position: absolute;
            bottom: 36px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 24px;
            pointer-events: none;
            z-index: 10;
        }}
        .badge {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 9999px;
            padding: 9px 22px;
            color: #94a3b8;
            font-size: 13.5px;
            font-weight: 500;
            letter-spacing: 0.3px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
        }}
        .badge span {{
            color: #38bdf8;
            font-weight: 600;
        }}
        .badge .dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #38bdf8;
            box-shadow: 0 0 10px #38bdf8;
        }}
    </style>
    <script>{three_js_code}</script>
</head>
<body>
    <div class="header">
        <h1>DexPad Precision 3D Enclosure</h1>
        <p>Engineered for <span>Raspberry Pi Pico 2 W</span> &bull; 100% Snapless Friction Fit &bull; Zero Outer Fasteners</p>
    </div>
    <div id="canvas"></div>
    <div class="overlay">
        <div class="badge"><div class="dot"></div><span>Assembled Unit</span> Flush Mated Enclosure</div>
        <div class="badge"><div class="dot"></div><span>4x Friction Pegs</span> Solid Self-Centering Alignment</div>
        <div class="badge"><div class="dot"></div><span>Stepped Relief</span> Precision Debossed DexPad Logo</div>
    </div>

    <script>
    function decodeBase64Float32(b64) {{
        const binStr = atob(b64);
        const len = binStr.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {{
            bytes[i] = binStr.charCodeAt(i);
        }}
        return new Float32Array(bytes.buffer);
    }}

    function createGeometry(posB64, normB64) {{
        const pos = decodeBase64Float32(posB64);
        const norm = decodeBase64Float32(normB64);
        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
        geom.setAttribute('normal', new THREE.BufferAttribute(norm, 3));
        
        // Center in CAD XY (Width: 25.1mm -> 12.55, Length: 56.6mm -> 28.3)
        geom.translate(-12.55, -28.3, 0);
        
        // Transform CAD (Z up, Y forward, X right) to Three.js (Y up, -Z forward, X right)
        geom.applyMatrix4(new THREE.Matrix4().set(
            1,  0,  0, 0,
            0,  0,  1, 0,
            0, -1,  0, 0,
            0,  0,  0, 1
        ));
        
        geom.computeVertexNormals();
        return geom;
    }}

    const bottomGeom = createGeometry("{b_pos}", "{b_norm}");
    const topGeom = createGeometry("{t_pos}", "{t_norm}");

    // Scene Setup
    const container = document.getElementById('canvas');
    const scene = new THREE.Scene();

    // Cinematic perspective camera (moved back for comfortable framing and breathing room)
    const camera = new THREE.PerspectiveCamera(24, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.set(0, 66, 205);
    camera.lookAt(0, 12, 0);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true, powerPreference: 'high-performance' }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(2.0); // 2x supersampling for high fidelity
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.02; // Balanced natural photographic exposure
    container.appendChild(renderer.domElement);

    // Studio Ambient Light Pipeline
    const ambientLight = new THREE.AmbientLight(0x1e293b, 1.25);
    scene.add(ambientLight);

    // Key Light - Studio Warm Key with large soft shadow radius
    const keyLight = new THREE.DirectionalLight(0xfff7ed, 2.5);
    keyLight.position.set(-65, 120, 85);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 4096;
    keyLight.shadow.mapSize.height = 4096;
    keyLight.shadow.camera.near = 10;
    keyLight.shadow.camera.far = 320;
    keyLight.shadow.camera.left = -110;
    keyLight.shadow.camera.right = 110;
    keyLight.shadow.camera.top = 110;
    keyLight.shadow.camera.bottom = -110;
    keyLight.shadow.bias = -0.00015;
    keyLight.shadow.radius = 6.0; // Soft feathered shadow edge
    scene.add(keyLight);

    // Cyan Fill Light (Soft brand accent)
    const fillLight = new THREE.DirectionalLight(0x38bdf8, 1.15);
    fillLight.position.set(75, 50, 70);
    scene.add(fillLight);

    // Rear Specular Rim Light (Highlights top chamfers and logo relief)
    const rimLight = new THREE.DirectionalLight(0x94a3b8, 2.3);
    rimLight.position.set(0, 85, -95);
    scene.add(rimLight);

    // Ground Contact Shadow Receiver
    const floorGeo = new THREE.PlaneGeometry(600, 600);
    const floorMat = new THREE.ShadowMaterial({{ opacity: 0.38 }});
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = 0;
    floor.receiveShadow = true;
    scene.add(floor);

    // Subtle dark satin floor surface with soft reflection
    const groundMat = new THREE.MeshStandardMaterial({{
        color: 0x060910,
        roughness: 0.55,
        metalness: 0.20,
        transparent: true,
        opacity: 0.40
    }});
    const groundMesh = new THREE.Mesh(floorGeo, groundMat);
    groundMesh.rotation.x = -Math.PI / 2;
    groundMesh.position.y = -0.05;
    scene.add(groundMesh);

    // Photorealistic Plastic / Polymer Materials
    // 1. Sleek Matte Stealth Polymer (Deep Space Charcoal / Obsidian)
    const stealthPolymer = new THREE.MeshPhysicalMaterial({{
        color: 0x181f2a,
        roughness: 0.38,
        metalness: 0.04,
        clearcoat: 0.24,
        clearcoatRoughness: 0.20,
        reflectivity: 0.50,
    }});

    // 2. High-Tech Slate Polymer (Top Deck with subtle cyan undertone)
    const techSlatePolymer = new THREE.MeshPhysicalMaterial({{
        color: 0x1c2432,
        roughness: 0.36,
        metalness: 0.05,
        clearcoat: 0.26,
        clearcoatRoughness: 0.18,
        reflectivity: 0.52,
    }});

    // -------------------------------------------------------------------------
    // 1. LEFT GROUP: FULLY ASSEMBLED HERO DONGLE
    // -------------------------------------------------------------------------
    const assembledGroup = new THREE.Group();
    
    const heroBottom = new THREE.Mesh(bottomGeom, stealthPolymer);
    heroBottom.castShadow = true;
    heroBottom.receiveShadow = true;
    heroBottom.position.set(0, 0, 0);
    assembledGroup.add(heroBottom);

    const heroTop = new THREE.Mesh(topGeom, techSlatePolymer);
    heroTop.castShadow = true;
    heroTop.receiveShadow = true;
    heroTop.position.set(0, 4.5, 0); // Mated flush at Z = 4.5mm
    assembledGroup.add(heroTop);

    // Position Left, angled to showcase top debossed logo & front Micro-USB cutout
    assembledGroup.position.set(-38, 0, 4);
    // Rotate 122 deg for optimal logo lighting and front USB presentation
    assembledGroup.rotation.y = Math.PI * 0.68; 
    scene.add(assembledGroup);

    // -------------------------------------------------------------------------
    // 2. RIGHT GROUP: EXPLODED / ARCHITECTURAL VIEW (SHOWING 4 FRICTION PEGS)
    // -------------------------------------------------------------------------
    const explodedGroup = new THREE.Group();
    
    // Bottom Shell resting on table, 4 alignment friction pins pointing UP
    const expBottom = new THREE.Mesh(bottomGeom, stealthPolymer);
    expBottom.castShadow = true;
    expBottom.receiveShadow = true;
    expBottom.position.set(0, 0, 0);
    explodedGroup.add(expBottom);

    // Top Shell floating directly above at Y = 28mm, revealing internal pins & standoffs
    const expTop = new THREE.Mesh(topGeom, techSlatePolymer);
    expTop.castShadow = true;
    expTop.receiveShadow = true;
    expTop.position.set(0, 28, 0);
    explodedGroup.add(expTop);

    // 4x Alignment Guide Lines linking pins to sockets
    const pegCoords = [
        {{ x: -5.7, z: 24.25 }},
        {{ x:  5.7, z: 24.25 }},
        {{ x: -5.7, z: -22.75 }},
        {{ x:  5.7, z: -22.75 }}
    ];

    const guideMaterial = new THREE.LineDashedMaterial({{
        color: 0x38bdf8,
        dashSize: 1.4,
        gapSize: 0.9,
        opacity: 0.85,
        transparent: true,
        linewidth: 1
    }});

    pegCoords.forEach(pt => {{
        const points = [];
        points.push(new THREE.Vector3(pt.x, 6.1, pt.z));
        points.push(new THREE.Vector3(pt.x, 28, pt.z));
        const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
        const line = new THREE.Line(lineGeo, guideMaterial);
        line.computeLineDistances();
        explodedGroup.add(line);
        
        // Small glowing landing target ring at pin base
        const ringGeo = new THREE.RingGeometry(1.2, 1.8, 24);
        const ringMat = new THREE.MeshBasicMaterial({{
            color: 0x38bdf8,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.65
        }});
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = -Math.PI / 2;
        ring.position.set(pt.x, 6.15, pt.z);
        explodedGroup.add(ring);
    }});

    // Position Right, parallel angle
    explodedGroup.position.set(38, 0, 4);
    explodedGroup.rotation.y = Math.PI * 0.68;
    scene.add(explodedGroup);

    // Render loop
    renderer.render(scene, camera);
    window.RENDER_COMPLETE = true;
    </script>
</body>
</html>"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated standalone 3D showcase HTML: {HTML_PATH}")

def render_screenshot():
    print("Capturing 3D photorealistic render via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--use-gl=angle",
                "--use-angle=d3d11"
            ]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.5 # 2880x1620 ultra crisp output
        )
        page = context.new_page()
        
        url = "file:///" + HTML_PATH.replace("\\", "/")
        print(f"Loading {url}...")
        page.goto(url, wait_until="load", timeout=15000)
        
        # Wait until Three.js signals render complete
        page.wait_for_function("() => window.RENDER_COMPLETE === true", timeout=10000)
        page.wait_for_timeout(1000) # Ensure frame is fully drawn to swapchain
        
        os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
        page.screenshot(path=OUT_PNG)
        browser.close()
        
    im = Image.open(OUT_PNG)
    print(f"Successfully saved studio render: {im.size} at {OUT_PNG}")

if __name__ == "__main__":
    generate_html()
    render_screenshot()
