#!/usr/bin/env python3


from PIL import Image, ImageDraw, ImageFont, ImageFilter
 

text = "a"

# fnt = ImageFont.truetype('Arial.ttf', 15)  # windows
fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)  # Linux

for text in "bhoilx^":
    img = Image.new('RGB', (57, 80), color = 'black')
    d = ImageDraw.Draw(img)
    d.text((0,0), text, "white", fnt)
    img2 = img.filter(ImageFilter.GaussianBlur(radius=6))
    img2.save(f'{text}.jpg')
