"""在 kernel 中添加 .venv 的 site-packages 路径，然后测试渲染。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    code = r"""
import os, subprocess, time, sys

# 1. 确保 Xvfb 运行
os.environ['DISPLAY'] = ':99'
r = subprocess.run('ps aux | grep Xvfb | grep -v grep', capture_output=True, text=True, shell=True)
if not r.stdout.strip():
    subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

# 2. 添加 .venv 的 site-packages 到 sys.path
venv_site = '/mnt/workspace/JCIIOT_repo/.venv/lib/python3.12/site-packages'
if venv_site not in sys.path:
    sys.path.insert(0, venv_site)
print(f'Added: {venv_site}')

# 3. 设置 mujoco 环境
repo = '/mnt/workspace/JCIIOT_repo'
for p in [
    os.path.join(repo, 'JCIIOT', 'src'),
    os.path.join(repo, 'JCIIOT', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robosuite', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robomimic'),
    os.path.join(repo, 'JCIIOT'),
]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ['MUJOCO_GL'] = 'glfw'

# 4. 测试 import
print('\n--- Import test ---')
try:
    import mujoco
    print(f'mujoco {mujoco.__version__} OK')
    from mujoco import Renderer
    print('Renderer OK')
except Exception as e:
    print(f'FAIL: {e}')
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
    print(f'Render OK! shape={pixels.shape}')
    from PIL import Image
    Image.fromarray(pixels).save('/tmp/test_render.png')
    print('Saved /tmp/test_render.png')
except Exception as e:
    import traceback
    traceback.print_exc()
"""
    print(d.run_python(code, timeout=90))


if __name__ == "__main__":
    main()
