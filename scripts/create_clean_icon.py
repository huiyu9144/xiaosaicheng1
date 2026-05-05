from PIL import Image, ImageDraw
import math

SIZE = 1024
output_path = '/Users/a1/Desktop/小进度/小赛程/小赛程/小赛程/Assets.xcassets/AppIcon.appiconset/icon_processed.png'

# 创建纯黑色背景
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 255))
draw = ImageDraw.Draw(img)

cx, cy = SIZE // 2, SIZE // 2

# 足球外圆
outer_radius = 380
draw.ellipse([cx - outer_radius, cy - outer_radius, cx + outer_radius, cy + outer_radius], outline=(200, 180, 240, 255), width=25)

# 绘制六边形函数
def draw_hexagon(draw, center, radius, fill_color, outline_color=None, outline_width=0):
    points = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill_color, outline=outline_color)
    if outline_color and outline_width > 0:
        for i in range(6):
            draw.line([points[i], points[(i+1)%6]], fill=outline_color, width=outline_width)

# 中心黑色六边形
draw_hexagon(draw, (cx, cy), 90, (0, 0, 0, 255), (0, 0, 0, 255))

# 周围6个彩色六边形
colors = [
    (180, 160, 220, 255),  # 紫色
    (160, 220, 180, 255),  # 绿色
    (120, 200, 240, 255),  # 蓝色
    (180, 160, 220, 255),  # 紫色
    (160, 220, 180, 255),  # 绿色
    (120, 200, 240, 255),  # 蓝色
]

spacing = 155
hex_radius = 85

for i in range(6):
    angle = math.pi / 3 * i
    hx = cx + spacing * math.cos(angle)
    hy = cy + spacing * math.sin(angle)
    draw_hexagon(draw, (hx, hy), hex_radius, colors[i], (0, 0, 0, 255), 8)

# 连接线条
for i in range(6):
    angle = math.pi / 3 * i
    hx = cx + spacing * math.cos(angle)
    hy = cy + spacing * math.sin(angle)
    draw.line([(cx, cy), (hx, hy)], fill=(0, 0, 0, 255), width=12)

# 确保四角是纯黑色
mask_size = 100
draw.rectangle([0, 0, mask_size, 30], fill=(0, 0, 0, 255))
draw.rectangle([0, 0, 30, mask_size], fill=(0, 0, 0, 255))
draw.rectangle([SIZE - mask_size, 0, SIZE, 30], fill=(0, 0, 0, 255))
draw.rectangle([SIZE - 30, 0, SIZE, mask_size], fill=(0, 0, 0, 255))
draw.rectangle([0, SIZE - 30, mask_size, SIZE], fill=(0, 0, 0, 255))
draw.rectangle([0, SIZE - mask_size, 30, SIZE], fill=(0, 0, 0, 255))
draw.rectangle([SIZE - mask_size, SIZE - 30, SIZE, SIZE], fill=(0, 0, 0, 255))
draw.rectangle([SIZE - 30, SIZE - mask_size, SIZE, SIZE], fill=(0, 0, 0, 255))

# 保存处理后的图片
img.save(output_path, 'PNG')
print(f'处理完成，已保存到: {output_path}')
