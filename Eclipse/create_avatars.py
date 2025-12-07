#!/usr/bin/env python
"""
Script to create placeholder avatar images
"""
import os
from PIL import Image, ImageDraw, ImageFont
import sys

def create_avatar_placeholder(output_path, text, bg_color, text_color):
    # Create a 200x200 image with background color
    img = Image.new('RGB', (200, 200), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a circle (avatar shape)
    draw.ellipse([10, 10, 190, 190], outline=text_color, width=3)
    
    # Add text in the center
    try:
        # Try to use default font
        font = ImageFont.load_default()
    except:
        # If default font fails, use a simple font
        font = ImageFont.load_default()
    
    # Calculate text size and position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (200 - text_width) // 2
    y = (200 - text_height) // 2
    
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save the image
    img.save(output_path)
    print(f"Created placeholder image: {output_path}")

if __name__ == "__main__":
    # Create default user avatar
    create_avatar_placeholder(
        "user_default.png", 
        "USER", 
        (70, 130, 180),    # Steel Blue
        (255, 255, 255)    # White
    )
    
    # Create default room avatar
    create_avatar_placeholder(
        "room_default.png", 
        "ROOM", 
        (34, 139, 34),     # Forest Green
        (255, 255, 255)    # White
    )