"""直接在 DSW kernel 里执行 mujoco 渲染测试（不用 subprocess）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    # 直接在 kernel 里运行——设置环境变量后直接 import
    code = r"""
import os, subprocess, time, sys

# 1. 安装 Xvfb（如果没有）
r = subprocess.run('which Xvfb 2>/dev/null', capture_output=True, text=True, shell=True)
if not r.stdout.strip():
    print('Installing Xvfb...')
    r = subprocess.run('apt-get update -qq && apt-get install -y -qq xvfb 2>&1 | tail -3',
                       capture_output=True, text=True, shell=True, timeout=120)
    print(r.stdout[-200:])

# 2. 启动 Xvfb
os.environ['DISPLAY'] = ':99'
subprocess.run('pkill Xvfb 2>/dev/null; sleep 1', shell=True)
subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
r = subprocess.run('ps aux | grep Xvfb | grep -v grep | head -1', capture_output=True, text=True, shell=True)
print(f'Xvfb: {"running" if r.stdout.strip() else "FAILED"}')

# 3. 设置环境
repo = '/mnt/workspace/JCIIOT_repo'
sys.path.insert(0, os.path.join(repo, 'JCIIOT', 'src'))
sys.path.insert(0, os.path.join(repo, 'JCIIOT', 'robosuite'))
sys.path.insert(0, os.path.join(repo, 'JCIIOT', 'robosuite', 'robosuite'))
sys.path.insert(0, os.path.join(repo, 'JCIIOT', 'robomimic'))
sys.path.insert(0, os.path.join(repo, 'JCIIOT'))
os.environ['MUJOCO_GL'] = 'glfw'

# 4. 测试 import
print('\n--- Import test ---')
try:
    import mujoco
    print(f'mujoco {mujoco.__version__} OK')
    from mujoco import Renderer
    print('Renderer import OK')
except Exception as e:
    print(f'Import FAIL: {e}')
    sys.exit(1)

# 5. 测试渲染
print('\n--- Render test ---')
try:
    xml = '<mujoco><worldbody><light pos="0 0 3"/><geom type="sphere" size="0.5"/></worldbody></mujoco>'
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    renderer = Renderer(model, height=120, width=160)
    mujoco.mj_forward(model, data)
    renderer.update_scene(data)
    pixels = renderer.render()
    print(f'Render OK! shape={pixels.shape}, dtype={pixels.dtype}')
    from PIL import Image
    Image.fromarray(pixels).save('/tmp/test_render.png')
    print('Saved /tmp/test_render.png')
except Exception as e:
    import traceback
    print(f'Render FAIL: {type(e).__name__}: {e}')
    traceback.print_exc()
"""
    print(d.run_python(code, timeout=120))


if __name__ == "__main__":
    main()
