from PIL import Image, ImageDraw, ImageFont
import random

text = "memdiff"
font = ImageFont.truetype("Arial", 24)

img = Image.new('RGB', (140, 45), color='#f0f0f0')
draw = ImageDraw.Draw(img)

# add noise lines
for _ in range(4):
    x1, y1 = random.randint(0, 140), random.randint(0, 45)
    x2, y2 = random.randint(0, 140), random.randint(0, 45)
    draw.line((x1, y1, x2, y2), fill=(150, 150, 150), width=1)

# write text with letter rotation
x_offset = 8
for letter in text:
    letter_img = Image.new('RGBA', (30, 35), (0, 0, 0, 0))
    letter_draw = ImageDraw.Draw(letter_img)
    letter_draw.text((5, 5), letter, font=font, fill=(50, 50, 100))
    angle = random.randint(-15, 15)
    letter_img = letter_img.rotate(angle, expand=False, resample=Image.BICUBIC)
    y_offset = random.randint(-3, 3)
    img.paste(letter_img, (x_offset, 5 + y_offset), letter_img)
    x_offset += 18

# add noisy points 
for _ in range(20):
    x, y = random.randint(0, 140), random.randint(0, 45)
    draw.point((x, y), fill=(100, 100, 100))

# save
img.save('captcha.jpg', 'JPEG', quality=60, optimize=True)