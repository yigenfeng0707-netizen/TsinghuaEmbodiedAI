"""
Stage 267: 安装系统级 EGL 库 + 验证 mujoco EGL 渲染
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dsw_remote import DswRemote


REMOTE_SCRIPT = r"""
import os, sys, subprocess

print("=" * 70)
print("STAGE 267: INSTALL EGL SYSTEM LIBS")
print("=" * 70)

# 1. 检查 GPU
print("\n[1] GPU check:")
result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=30)
print(result.stdout[:1000] if result.stdout else "no output")
print(result.stderr[:500] if result.stderr else "")

# 2. 检查现有 EGL 库
print("\n[2] Check existing EGL libs:")
result = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True, timeout=10)
for line in result.stdout.split("\n"):
    if "EGL" in line or "egl" in line:
        print(f"  {line}")

# 3. 查找 libEGL.so
print("\n[3] Find libEGL.so:")
result = subprocess.run(["find", "/usr", "-name", "libEGL*", "-type", "f"], capture_output=True, text=True, timeout=30)
print(result.stdout if result.stdout else "  not found")

# 4. 安装 EGL 系统库
print("\n[4] Installing EGL system libs:")
result = subprocess.run(
    ["apt-get", "update", "-qq"],
    capture_output=True, text=True, timeout=120
)
print(f"  apt update rc={result.returncode}")

result = subprocess.run(
    ["apt-get", "install", "-y", "-qq", "libegl1", "libgles2", "libgl1-mesa-glx", "libgl1-mesa-dri", "libegl-mesa0"],
    capture_output=True, text=True, timeout=300
)
print(f"  apt install rc={result.returncode}")
print(f"  stdout: {result.stdout[-500:] if result.stdout else ''}")
print(f"  stderr: {result.stderr[-500:] if result.stderr else ''}")

# 5. 再次查找 libEGL.so
print("\n[5] Find libEGL.so after install:")
result = subprocess.run(["find", "/usr", "-name", "libEGL*", "-type", "f"], capture_output=True, text=True, timeout=30)
print(result.stdout if result.stdout else "  not found")

# 6. 设置环境变量并测试
print("\n[6] Test mujoco with EGL:")
os.environ["MUJOCO_GL"] = "egl"
os.environ["PYOPENGL_PLATFORM"] = "egl"

# 清除已导入的模块
for mod_name in list(sys.modules.keys()):
    if "mujoco" in mod_name or "OpenGL" in mod_name:
        del sys.modules[mod_name]

try:
    import mujoco
    print(f"  [OK] mujoco imported, version: {mujoco.__version__}")

    # 测试渲染
    xml = "<mujoco><worldbody><light pos='0 0 3'/><geom type='sphere' size='0.5'/></worldbody></mujoco>"
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    renderer = mujoco.Renderer(model, 64, 64)
    mujoco.mj_forward(model, data)
    renderer.update_scene(data)
    img = renderer.render()
    print(f"  [OK] EGL rendering works, image shape: {img.shape}, dtype: {img.dtype}")
except Exception as e:
    print(f"  [FAIL] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n[DONE]")
"""


async def main():
    dsw = DswRemote()
    await dsw.connect()
    print("\n[Stage 267] 安装 EGL 系统库...")
    output = await dsw.execute_via_jupyter_api(REMOTE_SCRIPT, timeout=600)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())
