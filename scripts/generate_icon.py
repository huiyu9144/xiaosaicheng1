from PIL import Image, ImageDraw

SIZE = 1024
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 255))
draw = ImageDraw.Draw(img)

cx, cy = SIZE // 2, SIZE // 2
radius = 360

colors = [
    (180, 150, 220),
    (150, 220, 180),
    (120, 180, 220),
]

for i in range(10):
    r = radius - i * 35
    if r < 50:
        break
    color = colors[i % 3]
    alpha = max(40, 180 - i * 15)
    draw.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        outline=(*color, alpha),
        width=30
    )

draw.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=(0, 0, 0, 255))

output = '/Users/a1/Desktop/小进度/小赛程/小赛程/小赛程/Assets.xcassets/AppIcon.appiconset/icon_1024.png'
img.save(output, 'PNG')
print(f'Icon saved: {output}')
