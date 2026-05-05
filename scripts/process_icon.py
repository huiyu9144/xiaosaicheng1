from PIL import Image, ImageDraw
import os

# 查找原始图片
base_dir = '/Users/a1/Desktop/小进度/小赛程/小赛程/小赛程/Assets.xcassets/AppIcon.appiconset'
input_path = None

# 查找所有png文件
for file in os.listdir(base_dir):
    if file.endswith('.png') and 'icon_1024' not in file and 'icon_cleaned' not in file and 'icon_no_watermark' not in file:
        input_path = os.path.join(base_dir, file)
        break

if not input_path:
    print('未找到原始图片文件')
    exit(1)

output_path = os.path.join(base_dir, 'icon_processed.png')

# 打开图片
img = Image.open(input_path).convert('RGBA')
width, height = img.size

# 创建新图片，背景为纯黑色
new_img = Image.new('RGBA', (width, height), (0, 0, 0, 255))

# 复制原图内容到新图片
new_img.paste(img, (0, 0), img)

draw = ImageDraw.Draw(new_img)

# 去除右下角水印 - 用黑色矩形覆盖
# 水印在右下角，大约宽度200px，高度60px
watermark_x = width - 220
watermark_y = height - 70
draw.rectangle([watermark_x, watermark_y, width, height], fill=(0, 0, 0, 255))

# 确保整个背景都是黑色（处理边缘区域）
# 顶部边缘
draw.rectangle([0, 0, width, 15], fill=(0, 0, 0, 255))
# 底部边缘
draw.rectangle([0, height - 15, width, height], fill=(0, 0, 0, 255))
# 左侧边缘
draw.rectangle([0, 0, 15, height], fill=(0, 0, 0, 255))
# 右侧边缘
draw.rectangle([width - 15, 0, width, height], fill=(0, 0, 0, 255))

# 保存处理后的图片
new_img.save(output_path, 'PNG')
print(f'处理完成，已保存到: {output_path}')
