#!/usr/bin/env python3
"""
Create a simple Chappy icon
"""

from PIL import Image, ImageDraw
import math

def create_chappy_icon():
    """Create a brain/eye themed icon for Chappy"""
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    brain_color = (100, 149, 237, 255)  # Cornflower blue
    eye_color = (255, 255, 255, 255)    # White
    pupil_color = (0, 0, 0, 255)        # Black

    # Draw brain outline (simplified)
    center = size // 2
    radius = 100

    # Left hemisphere
    draw.ellipse([center-radius-20, center-radius, center-20, center+radius],
                fill=brain_color, outline=(70, 130, 180, 255), width=3)

    # Right hemisphere
    draw.ellipse([center+20, center-radius, center+radius+20, center+radius],
                fill=brain_color, outline=(70, 130, 180, 255), width=3)

    # Connecting tissue
    draw.rectangle([center-20, center-30, center+20, center+30], fill=brain_color)

    # Eye in center
    eye_radius = 25
    draw.ellipse([center-eye_radius, center-eye_radius, center+eye_radius, center+eye_radius],
                fill=eye_color, outline=(0, 0, 0, 255), width=2)

    # Pupil
    pupil_radius = 12
    draw.ellipse([center-pupil_radius, center-pupil_radius, center+pupil_radius, center+pupil_radius],
                fill=pupil_color)

    # Save icon
    img.save('desktop/icons/chappy_icon.png')
    print("Icon created: desktop/icons/chappy_icon.png")

if __name__ == "__main__":
    create_chappy_icon()