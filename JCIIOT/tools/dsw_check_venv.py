"""检查 DSW .venv 和 JCIIOT 目录结构。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    code = r"""
import os, subprocess

# 1. 检查 .venv
print('=== .venv packages ===')
venv_pip = '/mnt/workspace/JCIIOT_repo/.venv/bin/pip'
if os.path.exists(venv_pip):
    r = subprocess.run([venv_pip, 'list'], capture_output=True, text=True, timeout=30)
    for line in r.stdout.split('\n'):
        if any(k in line.lower() for k in ['mujoco', 'robosuite', 'robomimic', 'pillow', 'numpy', 'opencv', 'imageio']):
            print(f'  {line}')
else:
    print(f'  {venv_pip} not found')
    # 尝试 Windows 风格
    venv_pip2 = '/mnt/workspace/JCIIOT_repo/.venv/Scripts/pip.exe'
    if os.path.exists(venv_pip2):
        r = subprocess.run([venv_pip2, 'list'], capture_output=True, text=True, timeout=30)
        print(r.stdout[:500])
    else:
        print(f'  {venv_pip2} not found either')

# 2. 检查 JCIIOT 目录
print('\n=== JCIIOT_repo/JCIIOT ===')
jciiot = '/mnt/workspace/JCIIOT_repo/JCIIOT'
if os.path.exists(jciiot):
    for f in sorted(os.listdir(jciiot))[:30]:
        full = os.path.join(jciiot, f)
        t = 'DIR' if os.path.isdir(full) else 'FILE'
        print(f'  {t:4} {f}')

# 3. 检查 JCIIOT/src
print('\n=== JCIIOT/src ===')
src = os.path.join(jciiot, 'src')
if os.path.exists(src):
    for f in sorted(os.listdir(src))[:20]:
        print(f'  {f}')

# 4. 检查 robosuite_backend.py
print('\n=== Key files ===')
for p in [
    'JCIIOT/src/robot_agent/environments/robosuite_backend.py',
    'JCIIOT/app.py',
    'JCIIOT/requirements.txt',
    'JCIIOT/tools',
    'submission/trajectories',
]:
    full = os.path.join('/mnt/workspace/JCIIOT_repo', p)
    exists = os.path.exists(full)
    print(f'  {"OK" if exists else "MISS"}  {p}')
    if exists and os.path.isdir(full):
        items = os.listdir(full)
        print(f'       {len(items)} items: {items[:10]}')

# 5. 检查 submission/trajectories 里的 JSON
print('\n=== Trajectory files ===')
traj_dir = '/mnt/workspace/JCIIOT_repo/submission/trajectories'
if os.path.exists(traj_dir):
    for f in sorted(os.listdir(traj_dir)):
        size = os.path.getsize(os.path.join(traj_dir, f))
        print(f'  {f}  ({size//1024} KB)')
else:
    print('  NOT FOUND')
"""
    print(d.run_python(code, timeout=60))


if __name__ == "__main__":
    main()
