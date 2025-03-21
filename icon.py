#!/usr/bin/env python3
from PIL import Image, ImageDraw
import os

def create_icon():
    # Create a transparent image
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Define colors
    blue = (52, 152, 219, 255)  # Primary blue color
    white = (255, 255, 255, 255)  # White for the arrows
    
    # Draw blue circle (main background)
    margin = size // 8
    draw.ellipse(
        (margin, margin, size - margin, size - margin), 
        fill=blue
    )
    
    # Draw sync arrows
    arrow_width = size // 12
    arrow_length = size // 3
    arrow_padding = size // 8
    
    # Center of the icon
    center_x = size // 2
    center_y = size // 2
    
    # Top arrow (horizontal line)
    draw.rectangle(
        (
            center_x - arrow_length // 2,
            center_y - arrow_padding - arrow_width // 2,
            center_x + arrow_length // 2,
            center_y - arrow_padding + arrow_width // 2
        ),
        fill=white
    )
    
    # Bottom arrow (horizontal line)
    draw.rectangle(
        (
            center_x - arrow_length // 2,
            center_y + arrow_padding - arrow_width // 2,
            center_x + arrow_length // 2,
            center_y + arrow_padding + arrow_width // 2
        ),
        fill=white
    )
    
    # Save the icon as PNG with transparency
    icon_path = 'icon.png'
    img.save(icon_path)
    print(f"Icon created: {os.path.abspath(icon_path)}")

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw
        create_icon()
    except ImportError:
        print("Error: Please install Pillow first with 'pip install pillow'")
        print("Then run this script again to generate the icon.") 