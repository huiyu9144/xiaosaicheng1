from PIL import Image, ImageDraw
import math

SIZE = 1024
output_path = '/Users/a1/Desktop/小进度/小赛程/小赛程/小赛程/Assets.xcassets/AppIcon.appiconset/icon_final.png'

# 创建纯黑色背景
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 255))
draw = ImageDraw.Draw(img)

cx, cy = SIZE // 2, SIZE // 2

# 绘制一个带圆角的圆形背景（模拟图标的圆角效果）
# 使用渐变色圆形
outer_radius = 390
inner_radius = 380

# 绘制外圆环（渐变效果）
for r in range(outer_radius, inner_radius, -1):
    alpha = int(200 + (outer_radius - r) * 0.5)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(200, 180, 240, alpha))

# 足球图案
ball_radius = 370
draw.ellipse([cx - ball_radius, cy - ball_radius, cx + ball_radius, cy + ball_radius], outline=(200, 180, 240, 255), width=20)

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
draw_hexagon(draw, (cx, cy), 100, (0, 0, 0, 255), (0, 0, 0, 255))

# 周围6个彩色六边形
colors = [
    (180, 160, 220, 255),  # 紫色
    (160, 220, 180, 255),  # 绿色
    (120, 200, 240, 255),  # 蓝色
    (180, 160, 220, 255),  # 紫色
    (160, 220, 180, 255),  # 绿色
    (120, 200, 240, 255),  # 蓝色
]

spacing = 160
hex_radius = 90

for i in range(6):
    angle = math.pi / 3 * i
    hx = cx + spacing * math.cos(angle)
    hy = cy + spacing * math.sin(angle)
    draw_hexagon(draw, (hx, hy), hex_radius, colors[i], (0, 0, 0, 255), 10)

# 连接线条
for i in range(6):
    angle = math.pi / 3 * i
    hx = cx + spacing * math.cos(angle)
    hy = cy + spacing * math.sin(angle)
    draw.line([(cx, cy), (hx, hy)], fill=(0, 0, 0, 255), width=15)

# 确保四角是纯黑色
mask_size = 120
draw.rectangle([0, 0, mask_size, 40], fill=(0, 0, 0, 255))
draw.rectangle([0, 0, 40, mask_size], fill=(0, 0, 0, 255))
draw.rectangle([SIZE - mask_size, 0, SIZE, 40], fill=(0, 0, 0, 255))
draw.rectangle([SIZE - 40, 0, SIZE, mask_size], fill=(0, 0, 0, 255))
draw.rectangle([0, SIZE - 40, mask_size, SIZE], fill=(0, 0, 0, 255))
draw.rectangle([0, SIZE - mask_size, 40, SIZE], fill=(0, 0, 0, 255))
draw.rectangle([SIZE - mask_size, SIZE - 40, SIZE, SIZE], fill=(0, 0, 0, 255))
draw.rectangle([SIZE - 40, SIZE - mask_size, SIZE, SIZE], fill=(0, 0, 0, 255))

# 保存处理后的图片
img.save(output_path, 'PNG')
print(f'处理完成，已保存到: {output_path}')
