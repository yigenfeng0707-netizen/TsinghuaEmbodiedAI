"""检查 DSW 上 JCIIOT_repo 的内容，确认项目是否已存在。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    code = r"""
import os, subprocess

# 检查 JCIIOT_repo
print('=== JCIIOT_repo ===')
repo = '/mnt/workspace/JCIIOT_repo'
if os.path.exists(repo):
    for f in sorted(os.listdir(repo))[:30]:
        full = os.path.join(repo, f)
        t = 'DIR' if os.path.isdir(full) else 'FILE'
        print(f'  {t:4} {f}')
else:
    print('  NOT FOUND')

# 检查是否有 robosuite/mujoco 在某处
print('\n=== Search for mujoco/robosuite ===')
r = subprocess.run(
    'find /mnt/workspace -maxdepth 3 -name "robosuite" -type d 2>/dev/null | head -5; '
    'find /mnt/workspace -maxdepth 3 -name "mujoco" -type d 2>/dev/null | head -5',
    capture_output=True, text=True, shell=True, timeout=30
)
print(r.stdout or '(not found)')

# 检查 pip 已安装的包
print('\n=== Installed packages (relevant) ===')
r = subprocess.run(
    'pip list 2>/dev/null | grep -iE "mujoco|robosuite|robomimic|gymnasium|opencv|imageio"',
    capture_output=True, text=True, shell=True, timeout=15
)
print(r.stdout or '(none)')

# 检查是否有 robosuite 的 pip 安装记录
print('\n=== Check robosuite in site-packages ===')
r = subprocess.run(
    'python -c "import robosuite; print(robosuite.__file__)" 2>&1; '
    'python -c "import mujoco; print(mujoco.__file__)" 2>&1',
    capture_output=True, text=True, shell=True, timeout=15
)
print(r.stdout)

# 检查 JCIIOT_repo 里是否有 src/robosuite_backend.py
print('\n=== Check key files in JCIIOT_repo ===')
for sub in ['src/robot_agent/environments/robosuite_backend.py',
            'tools/batch_generate_replay_gifs.py',
            'app.py', 'requirements.txt']:
    full = os.path.join(repo, sub)
    print(f'  {"OK" if os.path.exists(full) else "MISS"}  {sub}')
"""
    print(d.run_python(code, timeout=60))


if __name__ == "__main__":
    main()
