#!/usr/bin/env python3
from PIL import Image, ImageDraw
import os

def generate_icon():
    # Create a 512x512 image with a transparent background
    icon_size = 512
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Define colors
    bg_color = (52, 152, 219)  # Blue
    
    # Draw a circle as the background
    draw.ellipse((0, 0, icon_size, icon_size), fill=bg_color)
    
    # Draw horizontal bars (PDF-like)
    bar_height = 40
    bar_spacing = 80
    bar_color = (255, 255, 255)  # White
    
    # First bar
    bar_y1 = (icon_size - bar_spacing) // 2 - bar_height
    bar_y2 = bar_y1 + bar_height
    draw.rectangle((icon_size // 4, bar_y1, icon_size - icon_size // 4, bar_y2), fill=bar_color)
    
    # Second bar
    bar_y1 = (icon_size + bar_spacing) // 2
    bar_y2 = bar_y1 + bar_height
    draw.rectangle((icon_size // 4, bar_y1, icon_size - icon_size // 4, bar_y2), fill=bar_color)
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Determine the resources directory (two levels up from utils folder)
    resources_dir = os.path.abspath(os.path.join(script_dir, "../../resources"))
    
    # Create resources directory if it doesn't exist
    os.makedirs(resources_dir, exist_ok=True)
    
    # Save the icon
    icon_path = os.path.join(resources_dir, "icon.png")
    icon.save(icon_path)
    
    return icon_path

if __name__ == "__main__":
    icon_path = generate_icon()
    print(f"Icon generated and saved to {icon_path}") 