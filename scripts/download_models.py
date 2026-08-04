#!/usr/bin/env python3
"""
Download BC policy checkpoints and demo data for reproduction.

由于模型 checkpoint 和 demo 数据较大（>100MB），不通过 git 提交。
本脚本支持三种下载方式：

方式 1: 从魔搭 DSW 实例下载（需要阿里云账号 + DSW 实例运行中）
  - 自动检测 DSW_URL 环境变量
  - 通过 JupyterLab API 下载文件

方式 2: 从 Hugging Face Hub 下载（推荐，公开访问）
  - 仓库: https://huggingface.co/datasets/jciiot/factory_sorting
  - 需要安装 huggingface_hub

方式 3: 重新训练（完全自主复现）
  - 参考 scripts/debug_stages/stage266_install_deps.py 安装依赖
  - 参考 modelscope-bc-self-train skill 进行 BC 训练

文件清单：
  - model_epoch_150.pth: BC_RNN policy checkpoint (800 epochs, L2 loss ~1.5e-5)
  - factory_sorting_grasp_50_fixed.hdf5: L1 训练数据 (50 episodes)
  - factory_sorting_grasp_202607201421.hdf5: L3 训练数据 (50 episodes)

放置位置：
  model_epoch_150.pth -> JCIIOT/robosuite/robosuite/
  *.hdf5 -> JCIIOT/demos_l1_50/ 或 JCIIOT/demos_l3_50/
"""
import argparse
import os
import sys
import hashlib
import shutil
import subprocess
from pathlib import Path
from typing import Optional


# 预期文件清单（相对路径, 预期大小 bytes, 预期 MD5）
EXPECTED_FILES = {
    "JCIIOT/robosuite/robosuite/model_epoch_150.pth": {
        "size": 141_860_000,
        "md5": None,  # 填入实际 MD5 后可校验
        "source": "bc_rnn_checkpoint",
    },
    "JCIIOT/demos_l1_50/factory_sorting_grasp_50_fixed.hdf5": {
        "size": None,
        "md5": None,
        "source": "l1_demos",
    },
    "JCIIOT/demos_l3_50/202607201421/factory_sorting_grasp_202607201421.hdf5": {
        "size": None,
        "md5": None,
        "source": "l3_demos",
    },
}


def md5sum(file_path: Path, chunk_size: int = 8192) -> str:
    """计算文件 MD5"""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def check_files(base_dir: Path) -> dict:
    """检查所有预期文件是否存在，返回状态字典"""
    status = {}
    print("Checking expected files:")
    for rel_path, info in EXPECTED_FILES.items():
        full = base_dir / rel_path
        file_status = {"exists": False, "size_ok": False, "md5_ok": None}
        if full.exists():
            file_status["exists"] = True
            actual_size = full.stat().st_size
            if info["size"]:
                if abs(actual_size - info["size"]) < 1_000_000:
                    file_status["size_ok"] = True
                    print(f"  [OK]   {rel_path} ({actual_size/1024/1024:.1f} MB)")
                else:
                    print(f"  [WARN] {rel_path}: size mismatch (got {actual_size}, expected ~{info['size']})")
            else:
                file_status["size_ok"] = True
                print(f"  [OK]   {rel_path} ({actual_size/1024/1024:.1f} MB)")

            if info["md5"]:
                actual_md5 = md5sum(full)
                if actual_md5 == info["md5"]:
                    file_status["md5_ok"] = True
                else:
                    file_status["md5_ok"] = False
                    print(f"  [WARN] {rel_path}: MD5 mismatch")
        else:
            print(f"  [MISS] {rel_path}")
        status[rel_path] = file_status
    return status


def download_from_huggingface(base_dir: Path, repo_id: str = "jciiot/factory_sorting") -> bool:
    """从 Hugging Face Hub 下载"""
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("[ERROR] huggingface_hub 未安装，请运行: pip install huggingface_hub")
        return False

    print(f"\nDownloading from Hugging Face: {repo_id}")
    try:
        local_dir = base_dir / "downloads"
        local_dir.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=str(local_dir),
        )
        print(f"[OK] 下载完成，文件位于: {local_dir}")

        # 移动文件到预期位置
        for rel_path, info in EXPECTED_FILES.items():
            src_name = Path(rel_path).name
            src_file = local_dir / src_name
            if src_file.exists():
                dst_file = base_dir / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_file), str(dst_file))
                print(f"  Moved {src_name} -> {rel_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Hugging Face 下载失败: {e}")
        return False


def download_from_dsw(base_dir: Path, dsw_url: str) -> bool:
    """从魔搭 DSW 实例下载（需要 DSW 实例运行中）"""
    print(f"\nDownloading from DSW: {dsw_url}")
    print("[NOTE] 需要Chrome 已登录阿里云，且 DSW 实例正在运行")
    print("[NOTE] 此功能需要 dsw_remote.py 模块")

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import asyncio
        from dsw_remote import DswRemote

        async def _download():
            dsw = DswRemote()
            dsw.dsw_url = dsw_url
            await dsw.connect()

            remote_files = [
                ("/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/model_epoch_150.pth",
                 base_dir / "JCIIOT/robosuite/robosuite/model_epoch_150.pth"),
                ("/mnt/workspace/JCIIOT_repo/JCIIOT/demos_l1_50/factory_sorting_grasp_50_fixed.hdf5",
                 base_dir / "JCIIOT/demos_l1_50/factory_sorting_grasp_50_fixed.hdf5"),
                ("/mnt/workspace/JCIIOT_repo/JCIIOT/demos_l3_50/202607201421/factory_sorting_grasp_202607201421.hdf5",
                 base_dir / "JCIIOT/demos_l3_50/202607201421/factory_sorting_grasp_202607201421.hdf5"),
            ]

            for remote_path, local_path in remote_files:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    await dsw.download_file(remote_path, str(local_path))
                    print(f"  [OK] {remote_path} -> {local_path}")
                except Exception as e:
                    print(f"  [FAIL] {remote_path}: {e}")

            await dsw.close()

        asyncio.run(_download())
        return True
    except Exception as e:
        print(f"[ERROR] DSW 下载失败: {e}")
        print("[HINT] 请确保 dsw_remote.py 中的 DSW_URL 已更新为你的实例 URL")
        return False


def train_from_scratch(base_dir: Path) -> bool:
    """提示用户从零开始训练"""
    print("\n" + "=" * 70)
    print("训练 BC Policy 从零开始")
    print("=" * 70)
    print("""
推荐流程：
1. 启动 DSW GPU 实例（A10 23GB 或更高）
2. 安装依赖:
   cd scripts/debug_stages/
   python stage266_install_deps.py
   python stage267_install_egl.py
   python stage268_downgrade_numpy.py

3. 采集训练数据（50 episodes）:
   参考 modelscope-bc-self-train skill

4. 训练 BC RNN policy（800 epochs, ~13 分钟）:
   参考 bc_config_v4_lowdim.json 配置

5. 验证当前轨迹包:
   python stage264_test_champion_flow.py
""")
    return False


def main():
    parser = argparse.ArgumentParser(description="Download BC policy checkpoints and demo data")
    parser.add_argument("--base-dir", default=".", help="Base directory (default: current dir)")
    parser.add_argument("--source", choices=["huggingface", "dsw", "train"],
                        default="huggingface",
                        help="Download source (default: huggingface)")
    parser.add_argument("--dsw-url", default=os.environ.get("DSW_URL", ""),
                        help="DSW instance URL (for source=dsw)")
    parser.add_argument("--check-only", action="store_true",
                        help="Only check if files exist, don't download")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    print(f"Base directory: {base_dir}")

    # 检查现有文件
    status = check_files(base_dir)
    all_present = all(s["exists"] and s["size_ok"] for s in status.values())

    if all_present:
        print("\n[SUCCESS] All files present. Ready for reproduction.")
        return 0

    if args.check_only:
        print("\n[INFO] Some files missing. Run without --check-only to download.")
        return 1

    # 下载
    if args.source == "huggingface":
        success = download_from_huggingface(base_dir)
    elif args.source == "dsw":
        if not args.dsw_url:
            print("[ERROR] --dsw-url required for source=dsw")
            return 1
        success = download_from_dsw(base_dir, args.dsw_url)
    elif args.source == "train":
        success = train_from_scratch(base_dir)

    if success:
        # 再次检查
        print("\nVerifying downloaded files...")
        status = check_files(base_dir)
        all_present = all(s["exists"] and s["size_ok"] for s in status.values())
        if all_present:
            print("\n[SUCCESS] All files present. Ready for reproduction.")
            return 0
        else:
            print("\n[WARN] Some files still missing after download.")
            return 1
    else:
        print("\n[ERROR] Download failed. Try another source or train from scratch.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
