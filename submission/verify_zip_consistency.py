"""验证 Biendata validation zip 与本地 trajectories 目录的 JSON 哈希一致性。"""
import hashlib
import zipfile
from pathlib import Path

BASE = Path(__file__).parent  # submission/
ZIP_PATH = BASE / "biendata_validation" / "SOP-MapGuard_validation_trajectories.zip"
TRAJ_DIR = BASE / "trajectories"

print("=== Biendata validation zip vs local trajectories ===\n")

with zipfile.ZipFile(ZIP_PATH) as z:
    zip_files = sorted(z.namelist())
    print(f"Zip contains {len(zip_files)} files:")
    all_match = True
    for name in zip_files:
        zip_data = z.read(name)
        zip_md5 = hashlib.md5(zip_data).hexdigest()
        local_path = TRAJ_DIR / name
        if local_path.exists():
            local_data = local_path.read_bytes()
            local_md5 = hashlib.md5(local_data).hexdigest()
            match_str = "MATCH" if zip_md5 == local_md5 else "MISMATCH"
            if zip_md5 != local_md5:
                all_match = False
            print(f"  {name}: zip={zip_md5[:12]} local={local_md5[:12]} {match_str}")
        else:
            print(f"  {name}: zip={zip_md5[:12]} LOCAL_MISSING")
            all_match = False

print(f"\n=== Result: {'ALL MATCH' if all_match else 'HAS MISMATCH'} ===")

# 也检查 Final_Submission 目录里的轨迹
final_dir = BASE / "SOP-MapGuard_Final_Submission" / "trajectories"
if final_dir.exists():
    print(f"\n=== Final_Submission/trajectories vs zip ===")
    for name in zip_files:
        final_path = final_dir / name
        if final_path.exists():
            final_md5 = hashlib.md5(final_path.read_bytes()).hexdigest()
            match_str = "MATCH" if final_md5 == hashlib.md5(z.read(name)).hexdigest() else "MISMATCH"
            print(f"  {name}: {match_str}")
