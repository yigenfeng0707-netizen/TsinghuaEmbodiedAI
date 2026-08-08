"""上传 batch_generate_replay_gifs.py 到 DSW 并执行 GIF 生成。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    # 1. 检查 DSW 上是否已有 batch_generate_replay_gifs.py
    code = r"""
import os
p = '/mnt/workspace/JCIIOT_repo/JCIIOT/tools/batch_generate_replay_gifs.py'
print(f'Exists: {os.path.exists(p)}')
if os.path.exists(p):
    print(f'Size: {os.path.getsize(p)} bytes')
# 也检查 dsw_generate_gifs.sh
p2 = '/mnt/workspace/JCIIOT_repo/JCIIOT/tools/dsw_generate_gifs.sh'
print(f'dsw_generate_gifs.sh exists: {os.path.exists(p2)}')
"""
    print("=== 1. 检查脚本是否已存在 ===")
    print(d.run_python(code, timeout=15))

    # 2. 读取本地脚本内容，上传到 DSW
    local_script = Path(__file__).parent / "batch_generate_replay_gifs.py"
    if not local_script.exists():
        print(f"ERROR: {local_script} not found locally")
        return

    script_content = local_script.read_text(encoding="utf-8")
    print(f"\n=== 2. 上传脚本 ({len(script_content)} bytes) ===")

    # 用 JupyterLab Contents API 上传
    import requests
    import json

    upload_code = f"""
import json, base64
content = {json.dumps(script_content)!r}
path = '/mnt/workspace/JCIIOT_repo/JCIIOT/tools/batch_generate_replay_gifs.py'
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
import os
print(f'Uploaded: {{os.path.getsize(path)}} bytes')
"""
    print(d.run_python(upload_code, timeout=20))

    # 3. 创建输出目录
    print("\n=== 3. 创建输出目录 ===")
    print(d.run_python(
        "import os; os.makedirs('/mnt/workspace/JCIIOT_repo/submission/replay_gifs', exist_ok=True); print('OK')",
        timeout=10
    ))

    # 4. 执行 GIF 生成（用 .venv 的 python）
    print("\n=== 4. 启动 GIF 生成 ===")
    gen_code = r"""
import subprocess, os, sys

repo = '/mnt/workspace/JCIIOT_repo'
venv_python = os.path.join(repo, '.venv', 'bin', 'python')
if not os.path.exists(venv_python):
    venv_python = os.path.join(repo, '.venv', 'Scripts', 'python.exe')

jciiot = os.path.join(repo, 'JCIIOT')
traj_dir = os.path.join(repo, 'submission', 'trajectories')
out_dir = os.path.join(repo, 'submission', 'replay_gifs')

env = os.environ.copy()
env['PYTHONPATH'] = (
    os.path.join(jciiot, 'src') + ':' +
    os.path.join(jciiot, 'tools') + ':' +
    os.path.join(jciiot, 'robosuite') + ':' +
    os.path.join(jciiot, 'robosuite', 'robosuite') + ':' +
    os.path.join(jciiot, 'robomimic') + ':' +
    jciiot + ':' +
    env.get('PYTHONPATH', '')
)
env['MUJOCO_GL'] = 'egl'
env['PYOPENGL_PLATFORM'] = 'egl'
env['MUJOCO_EGL_DEVICE_ID'] = '0'

print(f'Python: {venv_python}')
print(f'CWD: {jciiot}')
print(f'Traj dir: {traj_dir}')
print(f'Out dir: {out_dir}')
print(f'PYTHONPATH: {env["PYTHONPATH"][:100]}...')
print()

# 先测试 import
r = subprocess.run(
    [venv_python, '-c',
     'import mujoco; print(f"mujoco {mujoco.__version__}"); '
     'import robosuite; print("robosuite OK"); '
     'from PIL import Image; print("PIL OK")'],
    capture_output=True, text=True, env=env, cwd=jciiot, timeout=30
)
print('Import test:')
print(r.stdout)
if r.stderr:
    print('STDERR:', r.stderr[:500])
if r.returncode != 0:
    print(f'Import FAILED (exit {r.returncode})')
    sys.exit(1)

print('\nStarting GIF generation...')
print('This may take 5-15 minutes...')
"""
    print(d.run_python(gen_code, timeout=60))


if __name__ == "__main__":
    main()
