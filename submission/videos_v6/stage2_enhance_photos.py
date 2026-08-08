#!/usr/bin/env python3
"""阶段2：照片增强 — 统一1920x1080 + 底部说明文字条 + 对比度/锐度提升。

原始GIF帧为640x480(4:3)，缩放后居中放置于1920x980区域，
底部100px黑色条显示关卡+视角说明文字。
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

SRC_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6\photos")
DST_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6\photos_enhanced")

TARGET_W, TARGET_H = 1920, 1080
IMG_AREA_H = 980  # 图片区域高度，底部100px留给文字条

# 关卡信息（基于task_config.json实际数据）
LEVEL_INFO = {
    "L1": {"name": "蓝色塑料盒搬运", "obj": "line_5_container_h01", "score": 10},
    "L2": {"name": "绿色储物箱搬运", "obj": "green_tote_b01",       "score": 15},
    "L3": {"name": "蓝色托盘搬运",   "obj": "blue_tote_b01",        "score": 20},
    "L4": {"name": "蓝色集装箱远端搬运", "obj": "blue_container_h01", "score": 25},
    "L5": {"name": "白色储物箱多件搬运", "obj": "white_tote_b01×3",  "score": 30},
}

VIEW_LABELS = {
    "grasp":    "抓取特写视角",
    "birdview": "鸟瞰回放视角",
    "robotview":"第一人称回放视角",
}


def find_font(size: int = 32) -> ImageFont.FreeTypeFont:
    """查找系统中文字体。"""
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
        r"C:\Windows\Fonts\msyhbd.ttc",    # Microsoft YaHei Bold
        r"C:\Windows\Fonts\simhei.ttf",    # SimHei
        r"C:\Windows\Fonts\simsun.ttc",    # SimSun
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def enhance_photo(src: Path, dst: Path, level: str, view: str, idx: int) -> None:
    """增强单张照片：缩放居中 + 深色边框 + 底部文字条 + 对比度/锐度。"""
    img = Image.open(src).convert("RGB")

    # 对比度 ×1.15, 锐度 ×1.25
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Sharpness(img).enhance(1.25)

    # 缩放保持比例到 IMG_AREA_H 高度内，宽度不超过 TARGET_W
    scale = min(TARGET_W / img.width, IMG_AREA_H / img.height)
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # 创建画布：深蓝黑背景
    canvas = Image.new("RGB", (TARGET_W, TARGET_H), (10, 10, 30))
    offset = ((TARGET_W - new_w) // 2, (IMG_AREA_H - new_h) // 2)
    canvas.paste(img, offset)

    # 底部文字条
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, IMG_AREA_H), (TARGET_W, TARGET_H)], fill=(0, 0, 0))

    font = find_font(30)
    info = LEVEL_INFO[level]
    view_label = VIEW_LABELS.get(view, view)
    caption = f"{level} | {info['name']} | {view_label} | 帧{idx:02d} | 满分{info['score']}分"
    draw.text((40, 1010), caption, font=font, fill=(255, 255, 255))

    canvas.save(dst, "PNG", quality=95)


def main() -> int:
    DST_DIR.mkdir(parents=True, exist_ok=True)
    total = 0

    for level in ["L1", "L2", "L3", "L4", "L5"]:
        level_src = SRC_DIR / level
        if not level_src.exists():
            continue
        level_dst = DST_DIR / level
        level_dst.mkdir(parents=True, exist_ok=True)

        for png in sorted(level_src.glob("*.png")):
            # 解析文件名：L1_grasp_01.png -> level=L1, view=grasp, idx=1
            parts = png.stem.split("_")
            level = parts[0]
            view = parts[1]
            idx = int(parts[2])
            dst = level_dst / png.name
            enhance_photo(png, dst, level, view, idx)
            total += 1
            print(f"  {png.name} -> {dst.name} OK")

    print(f"\n=== 完成：共增强 {total} 张照片 -> {DST_DIR} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
