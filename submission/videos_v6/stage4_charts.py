#!/usr/bin/env python3
"""阶段4：生成专业图表 — SOP参数表 + 得分可视化。

输出2张图表：
1. SOP参数表（5关 × 抓取策略/抬升高度/路径规划）
2. 得分堆叠柱状图（10+15+20+25+30=100）
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

OUT_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6\charts")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 中文字体
for f in ["Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei"]:
    if any(f in fp.name for fp in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [f]
        break
plt.rcParams["axes.unicode_minus"] = False

BG_COLOR = "#1a1a2e"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#e94560"


def gen_sop_table():
    """生成SOP参数表图表。"""
    cols = ["关卡", "物体类型", "抓取策略", "抬升(m)", "路径规划", "满分"]
    data = [
        ["L1", "蓝色塑料盒",     "双臂协同",   "0.15", "直接导航",  "10"],
        ["L2", "绿色储物箱",     "单臂焊接",   "跳过",  "直接导航",  "15"],
        ["L3", "蓝色托盘",       "单臂(迁移)", "跳过",  "策略复用",  "20"],
        ["L4", "蓝色集装箱",     "双臂协同",   "0.15", "A*远端",   "25"],
        ["L5", "白色储物箱×3",   "单臂循环",   "跳过",  "远端循环",  "30"],
    ]

    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")

    table = ax.table(cellText=data, colLabels=cols, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(16)
    table.scale(1, 3.5)

    # 表头样式
    for j in range(len(cols)):
        cell = table[0, j]
        cell.set_facecolor(ACCENT_COLOR)
        cell.set_text_props(color=TEXT_COLOR, fontweight="bold")
        cell.set_edgecolor("#ffffff")

    # 数据行样式
    for i in range(1, len(data) + 1):
        for j in range(len(cols)):
            cell = table[i, j]
            cell.set_facecolor("#16213e" if i % 2 == 0 else "#0f3460")
            cell.set_text_props(color=TEXT_COLOR)
            cell.set_edgecolor("#ffffff")

    plt.title("FactorySorting SOP 参数表", fontsize=28, color=TEXT_COLOR, pad=20, fontweight="bold")
    out_path = OUT_DIR / "sop_table.png"
    plt.savefig(out_path, dpi=100, facecolor=BG_COLOR, bbox_inches="tight", pad_inches=0.3)
    plt.close()
    print(f"  SOP参数表 -> {out_path}")
    return out_path


def gen_score_chart():
    """生成得分堆叠柱状图。"""
    levels = ["L1", "L2", "L3", "L4", "L5"]
    scores = [10, 15, 20, 25, 30]
    cumulative = np.cumsum(scores)

    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    colors = ["#0f3460", "#16213e", "#1a1a2e", "#533483", "#e94560"]
    bars = ax.bar(levels, scores, color=colors, edgecolor=TEXT_COLOR, linewidth=1.5)

    # 每关分数标注
    for bar, score, cum in zip(bars, scores, cumulative):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5, f"{score}分",
                ha="center", va="bottom", color=TEXT_COLOR, fontsize=18, fontweight="bold")
        ax.text(bar.get_x() + bar.get_width() / 2, h / 2, f"累计\n{cum}分",
                ha="center", va="center", color=TEXT_COLOR, fontsize=14)

    ax.set_ylabel("得分", fontsize=20, color=TEXT_COLOR)
    ax.set_title("五关得分进度（总分100分 · 满分通过）", fontsize=28, color=TEXT_COLOR, pad=20, fontweight="bold")
    ax.tick_params(colors=TEXT_COLOR, labelsize=16)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(TEXT_COLOR)
    ax.spines["left"].set_color(TEXT_COLOR)
    ax.set_ylim(0, 40)

    # 总分标注
    ax.text(4.4, 35, "100/100", fontsize=32, color=ACCENT_COLOR, fontweight="bold", ha="center")

    out_path = OUT_DIR / "score_chart.png"
    plt.savefig(out_path, dpi=100, facecolor=BG_COLOR, bbox_inches="tight", pad_inches=0.3)
    plt.close()
    print(f"  得分图 -> {out_path}")
    return out_path


def main() -> int:
    print("=== 生成专业图表 ===")
    gen_sop_table()
    gen_score_chart()
    print(f"=== 完成 -> {OUT_DIR} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
