import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_hero_banner(output_path=r"c:\Users\dwinslow\Documents\Dexter_Controller_Project\docs\dexpad_hero_banner.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), (6, 9, 18, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. Background radial nebula glows
    glow1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw1 = ImageDraw.Draw(glow1)
    gdraw1.ellipse([700, 80, 1150, 520], fill=(56, 189, 248, 55)) # Cyan glow under controller
    gdraw1.ellipse([150, 150, 550, 550], fill=(99, 102, 241, 45)) # Indigo glow behind title
    glow1 = glow1.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img, glow1)
    draw = ImageDraw.Draw(img)
    
    # 2. Draw modern grid accents
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 6), width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 6), width=1)
        
    # 3. Draw DexPad Logo mark
    logo_size = 110
    logo_img = Image.new("RGBA", (logo_size * 2, logo_size * 2), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(logo_img)
    
    # Cyan capsule
    cap = Image.new("RGBA", (logo_size * 2, logo_size * 2), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(cap)
    cdraw.rounded_rectangle([30, 85, 190, 135], radius=25, fill=(56, 189, 248, 255))
    cap_rot = cap.rotate(-45, resample=Image.BICUBIC, center=(110, 110))
    
    # White contoured stroke
    stroke = Image.new("RGBA", (logo_size * 2, logo_size * 2), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stroke)
    sdraw.rounded_rectangle([40, 88, 95, 132], radius=22, fill=(248, 250, 252, 255))
    sdraw.rounded_rectangle([125, 88, 180, 132], radius=22, fill=(248, 250, 252, 255))
    stroke_rot = stroke.rotate(45, resample=Image.BICUBIC, center=(110, 110))
    
    logo_combined = Image.alpha_composite(cap_rot, stroke_rot)
    img.paste(logo_combined, (70, 75), logo_combined)
    
    # 4. Typography
    try:
        font_title = ImageFont.truetype("segoeui.ttf", 64)
        font_sub = ImageFont.truetype("segoeuib.ttf", 26)
        font_desc = ImageFont.truetype("segoeui.ttf", 19)
        font_badge = ImageFont.truetype("segoeuib.ttf", 14)
    except:
        font_title = font_sub = font_desc = font_badge = ImageFont.load_default()
        
    # Brand Title
    draw.text((275, 100), "DexPad", font=font_title, fill=(255, 255, 255, 255))
    draw.text((275, 175), "Universal Controller Studio for macOS", font=font_sub, fill=(56, 189, 248, 255))
    
    # Pitch description
    desc_lines = [
        "Hardware-level Bluetooth gamepad bridge that natively translates PlayStation,",
        "Xbox, Nintendo Switch, and 8BitDo inputs into native USB keyboard and mouse.",
        "Zero drivers, zero kexts, and 100% compatibility with every Mac game."
    ]
    y_text = 240
    for line in desc_lines:
        draw.text((80, y_text), line, font=font_desc, fill=(160, 174, 192, 255))
        y_text += 30
        
    # Feature Badges
    badges = [
        "1-Click Pico 2 W Flasher",
        "Driverless USB Composite HID",
        "Auto Controller Sync",
        "RAWG Database",
        "Apache 2.0"
    ]
    bx = 80
    by = 360
    for b in badges:
        # Measure text width safely
        bbox = draw.textbbox((0, 0), b, font=font_badge)
        tw = bbox[2] - bbox[0]
        bw = tw + 24
        bh = 32
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(15, 23, 42, 220), outline=(56, 189, 248, 120), width=1)
        draw.text((bx + 12, by + 7), b, font=font_badge, fill=(224, 242, 254, 255))
        bx += bw + 12
        if bx > 520:
            bx = 80
            by += 44
            
    # Quick start banner callout
    callout_box = [80, 480, 560, 565]
    draw.rounded_rectangle(callout_box, radius=14, fill=(14, 165, 233, 25), outline=(56, 189, 248, 70), width=1)
    draw.text((100, 492), "SUPER SIMPLE 3-STEP SETUP", font=font_badge, fill=(56, 189, 248, 255))
    draw.text((100, 520), "1. Download DexPad  •  2. Hold BOOTSEL & Flash  •  3. Pair & Play", font=font_desc, fill=(255, 255, 255, 240))
    
    # 5. Right Side: Controller Visual Card
    # Load PS5 Neutral render if present
    ps5_path = r"c:\Users\dwinslow\Documents\Dexter_Controller_Project\app\src\assets\ps5\PS5_Front_Neutral.png"
    if os.path.exists(ps5_path):
        ps5 = Image.open(ps5_path).convert("RGBA")
        # Resize to fit in right half
        cw, ch = 520, int(520 * (ps5.height / ps5.width))
        ps5 = ps5.resize((cw, ch), Image.LANCZOS)
        
        # Add card surface behind controller
        card_box = [620, 80, 1140, 550]
        draw.rounded_rectangle(card_box, radius=24, fill=(15, 23, 42, 180), outline=(255, 255, 255, 30), width=1)
        
        # Draw mock UI header on card
        draw.rounded_rectangle([645, 105, 785, 140], radius=18, fill=(56, 189, 248, 30), outline=(56, 189, 248, 80), width=1)
        draw.text((660, 114), "PLAYSTATION 5", font=font_badge, fill=(56, 189, 248, 255))
        
        draw.rounded_rectangle([980, 105, 1115, 140], radius=18, fill=(34, 197, 94, 30), outline=(34, 197, 94, 80), width=1)
        draw.text((998, 114), "DONGLE READY", font=font_badge, fill=(74, 222, 128, 255))
        
        img.paste(ps5, (620, 175), ps5)
        
    img.save(output_path, "PNG")
    print(f"Generated {output_path} successfully ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    create_hero_banner()
