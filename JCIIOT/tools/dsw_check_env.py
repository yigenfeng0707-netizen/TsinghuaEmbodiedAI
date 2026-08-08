"""DSW 远程执行器：通过 dswhub.py 连接 DSW 并执行命令。"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    # 1. 检查项目文件
    print("=" * 60)
    print("1. 检查项目文件")
    print("=" * 60)
    check_code = r"""
import os
base = '/mnt/workspace'
for p in ['dswQinghua', 'dswQinghua/JCIIOT', 'dswQinghua/submission',
          'dswQinghua/submission/trajectories', 'dswQinghua/JCIIOT/tools']:
    full = os.path.join(base, p) if not p.startswith('/') else p
    # 尝试两种路径
    for try_path in [p, full, f'/mnt/workspace/{p}']:
        if os.path.exists(try_path):
            items = os.listdir(try_path)
            print(f'OK  {try_path} ({len(items)} items)')
            if 'trajectories' in try_path:
                for f in sorted(items):
                    print(f'     {f}')
            break
    else:
        print(f'MISS {p}')
"""
    print(d.run_python(check_code, timeout=30))

    # 2. 检查环境依赖
    print("=" * 60)
    print("2. 检查环境依赖")
    print("=" * 60)
    env_code = r"""
import sys
print(f'Python: {sys.version.split()[0]}')
for mod in ['mujoco', 'robosuite', 'PIL', 'numpy', 'gl']:
    try:
        m = __import__(mod)
        v = getattr(m, '__version__', 'ok')
        print(f'{mod}: {v}')
    except ImportError as e:
        print(f'{mod}: MISSING')
    except Exception as e:
        print(f'{mod}: ERROR ({e})')
"""
    print(d.run_python(env_code, timeout=30))

    # 3. 检查 GPU
    print("=" * 60)
    print("3. 检查 GPU")
    print("=" * 60)
    print(d.run_python(
        "import subprocess; r=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,memory.used','--format=csv,noheader'], capture_output=True, text=True); print(r.stdout or 'No GPU'); print(r.stderr[:200] if r.stderr else '')",
        timeout=20
    ))

    # 4. 检查轨迹文件
    print("=" * 60)
    print("4. 检查轨迹文件")
    print("=" * 60)
    traj_code = r"""
import os, glob
for base in ['/mnt/workspace/dswQinghua', '/mnt/workspace']:
    traj_dir = os.path.join(base, 'submission', 'trajectories')
    if os.path.exists(traj_dir):
        files = sorted(glob.glob(os.path.join(traj_dir, '*.json')))
        print(f'Trajectory dir: {traj_dir}')
        print(f'Found {len(files)} JSON files:')
        for f in files:
            size = os.path.getsize(f)
            print(f'  {os.path.basename(f)}  ({size//1024} KB)')
        break
else:
    print('No trajectory directory found')
"""
    print(d.run_python(traj_code, timeout=20))


if __name__ == "__main__":
    main()
