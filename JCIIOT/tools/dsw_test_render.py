"""测试 GLFW 渲染是否可用（可能需要 Xvfb），并尝试实际渲染一帧。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    code = r"""
import os, subprocess

# 1. 检查 Xvfb
print('=== Xvfb check ===')
r = subprocess.run('which Xvfb 2>/dev/null || echo NOT_FOUND', capture_output=True, text=True, shell=True)
print(f'Xvfb: {r.stdout.strip()}')
r = subprocess.run('which xvfb-run 2>/dev/null || echo NOT_FOUND', capture_output=True, text=True, shell=True)
print(f'xvfb-run: {r.stdout.strip()}')

# 2. 检查 DISPLAY
print(f'\nDISPLAY={os.environ.get("DISPLAY", "(unset)")}')

# 3. 检查是否有 X server 在跑
r = subprocess.run('ps aux | grep -E "Xvfb|Xorg" | grep -v grep', capture_output=True, text=True, shell=True)
print(f'X processes: {r.stdout.strip() or "(none)"}')

# 4. 尝试启动 Xvfb
print('\n=== Starting Xvfb ===')
r = subprocess.run('Xvfb :99 -screen 0 1024x768x24 & sleep 2 && echo XVFB_STARTED', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)
os.environ['DISPLAY'] = ':99'

# 5. 用 GLFW 测试实际渲染
print('\n=== Test GLFW render ===')
venv_python = '/mnt/workspace/JCIIOT_repo/.venv/bin/python'
repo = '/mnt/workspace/JCIIOT_repo'
env = os.environ.copy()
env['MUJOCO_GL'] = 'glfw'
env['DISPLAY'] = ':99'
env['PYTHONPATH'] = ':'.join([
    os.path.join(repo, 'JCIIOT', 'src'),
    os.path.join(repo, 'JCIIOT', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robosuite', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robomimic'),
    os.path.join(repo, 'JCIIOT'),
])

test_code = """
import os
print(f'MUJOCO_GL={os.environ.get("MUJOCO_GL")}')
print(f'DISPLAY={os.environ.get("DISPLAY")}')
try:
    import mujoco
    from mujoco import Renderer
    print('mujoco + Renderer imported OK')

    # 创建一个简单的模型并渲染
    xml = '''
    <mujoco>
      <worldbody>
        <light pos="0 0 3"/>
        <geom type="sphere" size="0.5" pos="0 0 0"/>
        <camera name="cam" pos="0 -2 1" quat="0.7 0 0 0.7"/>
      </worldbody>
    </mujoco>
    '''
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    renderer = Renderer(model, height=240, width=320)
    mujoco.mj_forward(model, data)
    renderer.update_scene(data, camera='cam')
    pixels = renderer.render()
    print(f'Render OK! shape={pixels.shape}, dtype={pixels.dtype}')
    print(f'Pixel sample: {pixels[100, 160].tolist()}')

    # 保存测试图
    from PIL import Image
    img = Image.fromarray(pixels)
    img.save('/tmp/test_render.png')
    print('Saved /tmp/test_render.png')

except Exception as e:
    import traceback
    print(f'RENDER FAIL: {type(e).__name__}: {e}')
    traceback.print_exc()
"""
r = subprocess.run([venv_python, '-c', test_code],
                   capture_output=True, text=True, env=env,
                   cwd=os.path.join(repo, 'JCIIOT'), timeout=30)
print(r.stdout)
if r.stderr:
    print('STDERR:', r.stderr[:800])
"""
    print(d.run_python(code, timeout=90))


if __name__ == "__main__":
    main()
