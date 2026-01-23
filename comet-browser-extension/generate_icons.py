#!/usr/bin/env python3
"""
Icon generator for Comet Browser VCS Extension
Converts SVG icon to required PNG sizes
"""

import os
import subprocess
import sys
from pathlib import Path

def generate_icons():
    """Generate PNG icons from SVG for Chrome extension"""

    icon_sizes = [16, 32, 48, 128]
    svg_path = Path(__file__).parent / "icons" / "icon.svg"
    icons_dir = Path(__file__).parent / "icons"

    if not svg_path.exists():
        print(f"Error: {svg_path} not found")
        return False

    # Check if ImageMagick or rsvg-convert is available
    converters = [
        ["rsvg-convert", "-h", "128", str(svg_path), "-o", "/tmp/test.png"],
        ["convert", str(svg_path), "-resize", "128x128", "/tmp/test.png"],
        ["inkscape", "--export-type=png", f"--export-filename=/tmp/test.png", str(svg_path)]
    ]

    converter_cmd = None
    for cmd in converters:
        try:
            result = subprocess.run(cmd[:2], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                converter_cmd = cmd
                break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    if not converter_cmd:
        print("Error: No suitable SVG to PNG converter found.")
        print("Please install one of:")
        print("  - rsvg-convert (librsvg)")
        print("  - ImageMagick (convert)")
        print("  - Inkscape")
        print("\nOr manually convert icon.svg to PNG files in sizes: 16x16, 32x32, 48x48, 128x128")
        return False

    print("Generating PNG icons...")

    for size in icon_sizes:
        png_path = icons_dir / f"icon{size}.png"

        if converter_cmd[0] == "rsvg-convert":
            cmd = ["rsvg-convert", "-h", str(size), "-w", str(size), str(svg_path), "-o", str(png_path)]
        elif converter_cmd[0] == "convert":
            cmd = ["convert", str(svg_path), "-resize", f"{size}x{size}", str(png_path)]
        elif converter_cmd[0] == "inkscape":
            cmd = ["inkscape", "--export-type=png", f"--export-filename={png_path}",
                   f"--export-width={size}", f"--export-height={size}", str(svg_path)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✓ Generated {png_path.name}")
            else:
                print(f"✗ Failed to generate {png_path.name}: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout generating {png_path.name}")
            return False

    print("\nIcon generation complete!")
    return True

def create_fallback_icons():
    """Create simple colored squares as fallback icons"""
    print("Creating fallback icons...")

    icon_sizes = [16, 32, 48, 128]
    icons_dir = Path(__file__).parent / "icons"

    for size in icon_sizes:
        png_path = icons_dir / f"icon{size}.png"

        # Create a simple colored square using Python PIL if available
        try:
            from PIL import Image, ImageDraw

            # Create image with gradient-like effect
            img = Image.new('RGB', (size, size), color='#667eea')
            draw = ImageDraw.Draw(img)

            # Draw a simple comet-like shape
            center = size // 2
            # Comet tail
            for i in range(5):
                alpha = 255 - (i * 40)
                draw.ellipse([center-2-i, center-8-i, center+2+i, center+8+i],
                           fill=(255-alpha//3, 107+alpha//6, 107+alpha//6))

            # Comet head
            draw.ellipse([center-3, center-3, center+3, center+3], fill='white')

            img.save(str(png_path))
            print(f"✓ Created fallback {png_path.name}")

        except ImportError:
            print("PIL not available, skipping fallback icon creation")
            break

if __name__ == "__main__":
    print("Comet Browser VCS Extension - Icon Generator")
    print("=" * 50)

    if not generate_icons():
        print("\nTrying fallback icon generation...")
        create_fallback_icons()

    print("\nTo use the extension:")
    print("1. Open Chrome and go to chrome://extensions/")
    print("2. Enable 'Developer mode'")
    print("3. Click 'Load unpacked' and select the comet-browser-extension folder")
    print("4. The extension should now be installed!")