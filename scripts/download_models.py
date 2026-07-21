#!/usr/bin/env python3
"""
Download BC policy checkpoints and demo data for reproduction.

由于模型 checkpoint 和 demo 数据较大（>100MB），不通过 git 提交。
请通过以下方式之一获取：

方式 1: 从魔搭 DSW 实例下载（需要阿里云账号）
  1. 启动 DSW GPU 实例（A10 23GB 或更高）
  2. /mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/model_epoch_150.pth
  3. /mnt/workspace/JCIIOT_repo/JCIIOT/demos_l1_50/factory_sorting_grasp_50_fixed.hdf5
  4. /mnt/workspace/JCIIOT_repo/JCIIOT/demos_l3_50/202607201421/factory_sorting_grasp_202607201421.hdf5

方式 2: 重新训练（推荐）
  参考 scripts/debug_stages/stage266_install_deps.py 安装依赖
  参考 modelscope-bc-self-train skill 进行 BC 训练

文件用途：
  - model_epoch_150.pth: BC_RNN policy checkpoint (800 epochs, L2 loss ~1.5e-5)
  - factory_sorting_grasp_50_fixed.hdf5: L1 训练数据 (50 episodes)
  - factory_sorting_grasp_202607201421.hdf5: L3 训练数据 (50 episodes)

放置位置：
  model_epoch_150.pth -> JCIIOT/robosuite/robosuite/
  *.hdf5 -> JCIIOT/demos_l1_50/ 或 JCIIOT/demos_l3_50/
"""
import os
import sys
from pathlib import Path

# 预期文件清单
EXPECTED_FILES = {
    "JCIIOT/robosuite/robosuite/model_epoch_150.pth": 141_860_000,  # ~141 MB
    "JCIIOT/demos_l1_50/factory_sorting_grasp_50_fixed.hdf5": None,
    "JCIIOT/demos_l3_50/202607201421/factory_sorting_grasp_202607201421.hdf5": None,
}

def check_files(base_dir: str = ".") -> bool:
    """检查所有预期文件是否存在"""
    base = Path(base_dir)
    all_found = True
    print("Checking expected files:")
    for rel_path, expected_size in EXPECTED_FILES.items():
        full = base / rel_path
        if full.exists():
            actual_size = full.stat().st_size
            if expected_size and abs(actual_size - expected_size) > 1_000_000:
                print(f"  [WARN] {rel_path}: size mismatch (got {actual_size}, expected ~{expected_size})")
            else:
                print(f"  [OK]   {rel_path} ({actual_size/1024/1024:.1f} MB)")
        else:
            print(f"  [MISS] {rel_path}")
            all_found = False
    return all_found

if __name__ == "__main__":
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if check_files(base_dir):
        print("\nAll files found. Ready for reproduction.")
        sys.exit(0)
    else:
        print("\nSome files missing. See instructions above to download.")
        sys.exit(1)
