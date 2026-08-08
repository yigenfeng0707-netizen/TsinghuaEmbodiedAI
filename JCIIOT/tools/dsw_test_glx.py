"""快速测试 MUJOCO_GL=glx 是否能让 robosuite 的 offscreen 渲染工作。

根因: robosuite binding_utils.py 第37行,若 macros.MUJOCO_GPU_RENDERING=True
且 MUJOCO_GL not in ["osmesa","glx"],会强制 MUJOCO_GL="egl"。
设为 glx 可跳过强制 EGL,走 GLFWGLContext(配合 Xvfb)。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub

# 测试脚本: 用 robosuite 自己的 MjRenderContextOffscreen 渲染一帧
_TEST_SCRIPT = r"""import os, sys
print(f'MUJOCO_GL={os.environ.get("MUJOCO_GL")}')
print(f'DISPLAY={os.environ.get("DISPLAY","(unset)")}')

# 在 import robosuite 之前检查 macros
sys.path.insert(0, '/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite')
import robosuite.macros as macros
print(f'MUJOCO_GPU_RENDERING={macros.MUJOCO_GPU_RENDERING}')

# 现在导入渲染相关
from robosuite.utils.binding_utils import MjSim, MjRenderContextOffscreen
import mujoco
import numpy as np

# 创建一个简单的 sim
xml = '<mujoco><worldbody><light pos="0 0 3"/><geom type="sphere" size="0.5" pos="0 0 0"/><camera name="cam" pos="0 -2 1" quat="0.7 0 0 0.7"/></worldbody></mujoco>'
model = mujoco.MjModel.from_xml_string(xml)
data = mujoco.MjData(model)

# 用 robosuite 的 MjSim 包装
class FakeModel:
    def __init__(self, m):
        self._model = m
        self.vis = m.vis
class FakeData:
    def __init__(self, d):
        self._data = d
class FakeSim:
    def __init__(self, m, d):
        self.model = FakeModel(m)
        self.data = FakeData(d)
        self._render_context_offscreen = None
    def forward(self):
        mujoco.mj_forward(self.model._model, self.data._data)
    def add_render_context(self, ctx):
        self._render_context_offscreen = ctx

sim = FakeSim(model, data)
sim.forward()

print('Creating MjRenderContextOffscreen...')
ctx = MjRenderContextOffscreen(sim, device_id=-1, max_width=320, max_height=240)
print('Context created OK')

ctx.update_scene = lambda *a, **kw: None  # placeholder
# 直接用 mujoco API 渲染
mujoco.mjv_updateScene(model, data, mujoco.MjvOption(), mujoco.MjvPerturb(),
                       ctx.cam, mujoco.mjtCatBit.mjCAT_ALL, ctx.scn)
mujoco.mjr_render(viewport=mujoco.MjrRect(0,0,320,240), scn=ctx.scn, con=ctx.con)
rgb = np.empty((240,320,3), dtype=np.uint8)
mujoco.mjr_readPixels(rgb=rgb, depth=None, viewport=mujoco.MjrRect(0,0,320,240), con=ctx.con)
print(f'RENDER OK! shape={rgb.shape}, pixel={rgb[100,160].tolist()}')

from PIL import Image
Image.fromarray(rgb).save('/tmp/test_glx_render.png')
print('Saved /tmp/test_glx_render.png')
"""


def main():
    d = Dswhub()

    # 上传测试脚本
    upload_code = (
        "import os\n"
        "path = '/tmp/test_glx_render.py'\n"
        f"content = {json.dumps(_TEST_SCRIPT)}\n"
        "with open(path, 'w', encoding='utf-8') as f:\n"
        "    f.write(content)\n"
        "print(f'Uploaded {os.path.getsize(path)} bytes')\n"
    )
    print(d.run_python(upload_code, timeout=20))

    # 运行测试
    code = r"""
import os, subprocess, time

# 确保 Xvfb 运行
os.environ['DISPLAY'] = ':99'
r = subprocess.run('ps aux | grep "[X]vfb" | head -1', capture_output=True, text=True, shell=True)
if not r.stdout.strip():
    subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    print('Xvfb started')
else:
    print('Xvfb already running')

repo = '/mnt/workspace/JCIIOT_repo'
venv_python = os.path.join(repo, '.venv', 'bin', 'python')
env = os.environ.copy()
env['MUJOCO_GL'] = 'glx'
env['DISPLAY'] = ':99'
env['PYTHONPATH'] = ':'.join([
    os.path.join(repo, 'JCIIOT', 'src'),
    os.path.join(repo, 'JCIIOT', 'tools'),
    os.path.join(repo, 'JCIIOT', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robosuite', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robomimic'),
    os.path.join(repo, 'JCIIOT'),
])

print('\n=== Running glx render test ===')
r = subprocess.run([venv_python, '/tmp/test_glx_render.py'],
                   capture_output=True, text=True, env=env,
                   cwd=os.path.join(repo, 'JCIIOT'), timeout=60)
print(r.stdout)
if r.stderr:
    err_lines = [l for l in r.stderr.split('\n') if l.strip() and 'Warning' not in l]
    if err_lines:
        print('STDERR:', '\n'.join(err_lines[:10]))
"""
    print(d.run_python(code, timeout=90))


if __name__ == "__main__":
    main()
