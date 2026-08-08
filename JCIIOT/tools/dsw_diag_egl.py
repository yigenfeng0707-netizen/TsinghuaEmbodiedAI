"""诊断 DSW 上 mujoco EGL 渲染问题并找到可用方案。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    code = r"""
import os, subprocess

# 1. 检查 EGL 库
print('=== EGL libraries ===')
r = subprocess.run('ldconfig -p 2>/dev/null | grep -iE "EGL|GL|osmesa"', capture_output=True, text=True, shell=True, timeout=15)
print(r.stdout or '(none found)')

# 2. 检查 nvidia 驱动
print('\n=== NVIDIA driver ===')
r = subprocess.run('nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout or 'No driver')

# 3. 检查 EGL device
print('\n=== EGL devices ===')
for dev in ['/dev/nvidia0', '/dev/dri/renderD128', '/dev/dri/card0']:
    print(f'  {dev}: {"EXISTS" if os.path.exists(dev) else "MISSING"}')

# 4. 尝试不同 MUJOCO_GL 设置
print('\n=== Try different MUJOCO_GL ===')
venv_python = '/mnt/workspace/JCIIOT_repo/.venv/bin/python'
repo = '/mnt/workspace/JCIIOT_repo'
env = os.environ.copy()
env['PYTHONPATH'] = ':'.join([
    os.path.join(repo, 'JCIIOT', 'src'),
    os.path.join(repo, 'JCIIOT', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robosuite', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robomimic'),
    os.path.join(repo, 'JCIIOT'),
])

for gl_mode in ['egl', 'osmesa', 'glfw', '']:
    env2 = env.copy()
    if gl_mode:
        env2['MUJOCO_GL'] = gl_mode
        env2['PYOPENGL_PLATFORM'] = gl_mode
    else:
        env2.pop('MUJOCO_GL', None)
        env2.pop('PYOPENGL_PLATFORM', None)

    r = subprocess.run(
        [venv_python, '-c',
         'try:\n'
         '    import mujoco\n'
         '    from mujoco import Renderer\n'
         '    print("OK: mujoco + Renderer imported")\n'
         'except Exception as e:\n'
         '    print(f"FAIL: {type(e).__name__}: {str(e)[:200]}")\n'],
        capture_output=True, text=True, env=env2, cwd=os.path.join(repo, 'JCIIOT'), timeout=20
    )
    label = gl_mode if gl_mode else '(unset)'
    print(f'  MUJOCO_GL={label:8}: {r.stdout.strip()}')
    if r.stderr and 'FAIL' in r.stdout:
        print(f'    stderr: {r.stderr[:200]}')
"""
    print(d.run_python(code, timeout=90))


if __name__ == "__main__":
    main()
