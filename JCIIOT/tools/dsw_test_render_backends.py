"""测试不同 MUJOCO_GL 后端(osmesa/egl/glfw)的 offscreen 渲染是否可用。

robosuite 的 sim.render() 用 MjRenderContextOffscreen(offscreen 渲染),
之前 MUJOCO_GL=glfw 只对 onscreen Renderer 有效,offscreen 仍回退到 EGL
然后失败。本脚本逐个测试 osmesa / egl / glfw(+Xvfb) 的 offscreen 渲染。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub

# 要上传到 DSW /tmp 的测试脚本(避免字符串嵌套问题)
_TEST_SCRIPT = r"""import os
print(f'  MUJOCO_GL={os.environ.get("MUJOCO_GL")}')
print(f'  DISPLAY={os.environ.get("DISPLAY","(unset)")}')
try:
    import mujoco
    print(f'  mujoco version: {mujoco.__version__}')

    xml = '<mujoco><worldbody><light pos="0 0 3"/><geom type="sphere" size="0.5" pos="0 0 0"/><camera name="cam" pos="0 -2 1" quat="0.7 0 0 0.7"/></worldbody></mujoco>'
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)

    # 测试 offscreen 渲染(MjRenderContextOffscreen, robosuite 用的就是这个)
    ctx = mujoco.MjRenderContextOffscreen(model, 240, 320)
    mujoco.mj_forward(model, data)
    ctx.update_scene(data, camera='cam')
    pixels = ctx.render()
    print(f'  OFFSCREEN OK! shape={pixels.shape}')
    print(f'  Pixel sample: {pixels[100, 160].tolist()}')
    ctx.free()
except Exception as e:
    print(f'  OFFSCREEN FAIL: {type(e).__name__}: {e}')
"""


def main():
    d = Dswhub()

    # 上传测试脚本到 /tmp
    upload_code = (
        "import os\n"
        "path = '/tmp/test_render_backend.py'\n"
        f"content = {json.dumps(_TEST_SCRIPT)}\n"
        "with open(path, 'w', encoding='utf-8') as f:\n"
        "    f.write(content)\n"
        "print(f'Uploaded {os.path.getsize(path)} bytes to ' + path)\n"
    )
    print("Uploading test script to /tmp...")
    print(d.run_python(upload_code, timeout=20))

    code = r"""
import os, subprocess, time

# 1. 杀掉旧的 GIF 生成进程
print('=== Killing old GIF process ===')
r = subprocess.run('pkill -f batch_generate_replay_gifs 2>/dev/null; sleep 1; pgrep -f batch_generate_replay_gifs || echo KILLED', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)

# 2. 确保 Xvfb 运行(给 glfw 测试用)
os.environ['DISPLAY'] = ':99'
r = subprocess.run('ps aux | grep "[X]vfb" | head -1', capture_output=True, text=True, shell=True)
if not r.stdout.strip():
    subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    print('Xvfb started')
else:
    print('Xvfb already running')

# 3. 检查 osmesa 库是否存在
print('\n=== osmesa library check ===')
r = subprocess.run('ldconfig -p 2>/dev/null | grep -i osmesa || echo NO_OSMESA_LIB', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)
r = subprocess.run('find /usr -name "libOSMesa*" 2>/dev/null | head -3 || echo NOT_FOUND', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)

# 4. 检查 EGL 库
print('\n=== EGL library check ===')
r = subprocess.run('ldconfig -p 2>/dev/null | grep -i "libEGL" | head -3 || echo NO_EGL_LIB', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)

# 5. 逐个测试渲染后端
repo = '/mnt/workspace/JCIIOT_repo'
venv_python = os.path.join(repo, '.venv', 'bin', 'python')
env_base = os.environ.copy()
env_base['PYTHONPATH'] = ':'.join([
    os.path.join(repo, 'JCIIOT', 'src'),
    os.path.join(repo, 'JCIIOT', 'tools'),
    os.path.join(repo, 'JCIIOT', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robosuite', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robomimic'),
    os.path.join(repo, 'JCIIOT'),
])

for backend in ['osmesa', 'egl', 'glfw']:
    print(f'\n=== Testing MUJOCO_GL={backend} ===')
    env = env_base.copy()
    env['MUJOCO_GL'] = backend
    if backend == 'glfw':
        env['DISPLAY'] = ':99'
    r = subprocess.run([venv_python, '/tmp/test_render_backend.py'],
                       capture_output=True, text=True, env=env,
                       cwd=os.path.join(repo, 'JCIIOT'), timeout=30)
    print(r.stdout)
    if r.stderr:
        err_lines = [l for l in r.stderr.split('\n') if l.strip() and 'Warning' not in l]
        if err_lines:
            print('  STDERR:', '\n  '.join(err_lines[:5]))
"""
    print(d.run_python(code, timeout=120))


if __name__ == "__main__":
    main()
