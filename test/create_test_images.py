#!/usr/bin/env python3

import platform
from PIL import Image, ImageDraw, ImageFont, ImageFilter
 
LETTERS = "bhoilx^"

# select font
if platform.system() == "Windows":
    fnt = ImageFont.truetype('ArialBold.ttf', 80) 
else:    
    fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)  



for text in LETTERS:
    
    # black background
    img = Image.new('RGB', (57, 80), color = 'black')
    d = ImageDraw.Draw(img)
    
    # draw white text
    d.text((0,0), text, "white", fnt)
    
    # blur
    img2 = img.filter(ImageFilter.GaussianBlur(radius=6))
    
    # save
    img2.save(f'{text}.jpg')
