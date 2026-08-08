#!/usr/bin/env python3
"""阶段3：生成修正后的叙事脚本。

关键修正：
- L3颜色从"橙色"改为"蓝色"（基于task_config.json实际数据 blue_tote_b01）
- 每句旁白配对对应照片素材 + Ken Burns镜头类型
- 三段式结构：任务概述 → 操作策略 → 结果总结
"""
from __future__ import annotations

import json
from pathlib import Path

PHOTO_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6\photos_enhanced")
OUT_FILE = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6\narration.json")


def p(level: str, name: str) -> str:
    """构造增强照片路径。"""
    return str(PHOTO_DIR / level / f"{level}_{name}.png")


# 叙事脚本：每句文本 + 对应照片 + Ken Burns镜头类型
# 镜头类型：in(缓慢放大) out(缓慢缩小) left(左移) right(右移) static(静态)
NARRATION = {
    "segments": [
        {
            "name": "intro",
            "lines": [
                {"text": "JCIIOT 2026 工业具身智能挑战赛。",       "photo": p("L1", "birdview_01"), "zoom": "in"},
                {"text": "五关FactorySorting满分实验全过程。",      "photo": p("L1", "birdview_02"), "zoom": "right"},
            ],
        },
        {
            "name": "L1",
            "lines": [
                {"text": "第一关，蓝色塑料盒搬运任务。",             "photo": p("L1", "birdview_01"), "zoom": "in"},
                {"text": "目标物体是蓝色空心塑料盒，位于近端生产线。",  "photo": p("L1", "birdview_02"), "zoom": "right"},
                {"text": "机器人从起始位置出发，沿最优路径导航。",     "photo": p("L1", "birdview_03"), "zoom": "left"},
                {"text": "采用双臂协同抓取策略，四指垫全接触。",      "photo": p("L1", "grasp_01"),    "zoom": "in"},
                {"text": "物理抬升零点一五米，验证抓取成功。",        "photo": p("L1", "grasp_02"),    "zoom": "static"},
                {"text": "沿规划路径运输至放置工位。",               "photo": p("L1", "birdview_04"), "zoom": "right"},
                {"text": "精准放置，偏差小于十毫米。",               "photo": p("L1", "grasp_03"),    "zoom": "out"},
                {"text": "第一关获得满分十分。",                    "photo": p("L1", "birdview_04"), "zoom": "static"},
            ],
        },
        {
            "name": "L2",
            "lines": [
                {"text": "第二关，绿色储物箱搬运任务。",             "photo": p("L2", "birdview_01"), "zoom": "in"},
                {"text": "目标物体是绿色镶边储物箱，体积较大。",      "photo": p("L2", "birdview_02"), "zoom": "right"},
                {"text": "机器人导航至拾取工位，准备抓取。",         "photo": p("L2", "robotview_01"),"zoom": "left"},
                {"text": "采用单臂抓取策略，跳过物理抬升。",         "photo": p("L2", "grasp_01"),    "zoom": "in"},
                {"text": "这种策略针对托盘类物体优化，效率更高。",    "photo": p("L2", "grasp_02"),    "zoom": "static"},
                {"text": "沿规划路径运输至放置工位。",               "photo": p("L2", "robotview_03"),"zoom": "right"},
                {"text": "第二关获得满分十五分。",                  "photo": p("L2", "birdview_04"), "zoom": "out"},
            ],
        },
        {
            "name": "L3",
            "lines": [
                # ✅ 修正：蓝色托盘（原srt误为"橙色"）
                {"text": "第三关，蓝色托盘搬运任务。",               "photo": p("L3", "birdview_01"), "zoom": "in"},
                {"text": "目标物体是蓝色托盘，与第二关物体类型相似。",  "photo": p("L3", "birdview_02"), "zoom": "right"},
                {"text": "机器人复用第二关训练好的策略，实现跨关卡迁移。", "photo": p("L3", "robotview_01"),"zoom": "left"},
                {"text": "无需重新训练，直接调用已有策略。",          "photo": p("L3", "grasp_01"),    "zoom": "in"},
                {"text": "单臂抓取，运输至放置工位。",               "photo": p("L3", "robotview_03"),"zoom": "right"},
                {"text": "精准放置，验证策略迁移成功。",              "photo": p("L3", "birdview_04"), "zoom": "out"},
                {"text": "第三关获得满分二十分。",                  "photo": p("L3", "grasp_03"),    "zoom": "static"},
            ],
        },
        {
            "name": "L4",
            "lines": [
                {"text": "第四关，蓝色集装箱远端搬运任务。",          "photo": p("L4", "birdview_01"), "zoom": "in"},
                {"text": "目标物体是蓝色空心塑料箱，位于远端生产线。",  "photo": p("L4", "birdview_02"), "zoom": "right"},
                {"text": "机器人需要跨厂区导航，路径更长更复杂。",     "photo": p("L4", "robotview_01"),"zoom": "left"},
                {"text": "采用双臂抓取策略，物理抬升零点一五米。",    "photo": p("L4", "grasp_01"),    "zoom": "in"},
                {"text": "A星路径规划算法确保最优导航轨迹。",        "photo": p("L4", "robotview_03"),"zoom": "right"},
                {"text": "运输至放置工位，全程稳定。",               "photo": p("L4", "birdview_04"), "zoom": "out"},
                {"text": "第四关获得满分二十五分。",                 "photo": p("L4", "grasp_03"),    "zoom": "static"},
            ],
        },
        {
            "name": "L5",
            "lines": [
                {"text": "第五关，白色储物箱多件搬运任务。",          "photo": p("L5", "birdview_01"), "zoom": "in"},
                {"text": "目标物体是三件白色边缘储物箱。",            "photo": p("L5", "birdview_02"), "zoom": "right"},
                {"text": "机器人需连续完成三次抓取与放置操作。",      "photo": p("L5", "robotview_01"),"zoom": "left"},
                {"text": "导航至最远端拾取工位。",                  "photo": p("L5", "robotview_02"),"zoom": "in"},
                {"text": "单臂抓取，逐件搬运至放置工位。",            "photo": p("L5", "grasp_01"),    "zoom": "right"},
                {"text": "三次操作均精准完成，无一失误。",            "photo": p("L5", "robotview_04"),"zoom": "out"},
                {"text": "第五关获得满分三十分。",                  "photo": p("L5", "birdview_04"), "zoom": "static"},
            ],
        },
        {
            "name": "outro",
            "lines": [
                {"text": "五关总分一百分，满分通过。",               "photo": p("L5", "birdview_04"), "zoom": "in"},
                {"text": "清华具身智能，JCIIOT 2026。",              "photo": p("L1", "birdview_01"), "zoom": "out"},
            ],
        },
    ]
}


def main() -> int:
    # 验证所有照片路径存在
    missing = []
    total_lines = 0
    for seg in NARRATION["segments"]:
        for line in seg["lines"]:
            total_lines += 1
            if not Path(line["photo"]).exists():
                missing.append(line["photo"])

    if missing:
        print(f"[ERROR] 缺失 {len(missing)} 张照片：")
        for m in missing:
            print(f"  {m}")
        return 1

    OUT_FILE.write_text(json.dumps(NARRATION, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"=== 完成：{total_lines} 句旁白 -> {OUT_FILE} ===")
    print(f"  片头: {len(NARRATION['segments'][0]['lines'])} 句")
    for i, seg in enumerate(NARRATION["segments"][1:6], 1):
        print(f"  {seg['name']}: {len(seg['lines'])} 句")
    print(f"  片尾: {len(NARRATION['segments'][6]['lines'])} 句")
    print("\n关键修正：")
    print("  L3颜色：橙色 → 蓝色（基于 task_config.json: blue_tote_b01）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
