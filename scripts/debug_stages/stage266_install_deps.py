"""
Stage 266: 新实例安装环境依赖（mujoco, robosuite, robomimic 等）
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dsw_remote import DswRemote


REMOTE_SCRIPT = r"""
import os, sys, subprocess

print("=" * 70)
print("STAGE 266: INSTALL DEPENDENCIES ON NEW INSTANCE")
print("=" * 70)

# 1. 检查当前 Python 环境
print("\n[1] Python environment:")
print(f"  Python: {sys.version}")
print(f"  Executable: {sys.executable}")

# 2. 检查已安装的关键包
print("\n[2] Checking installed packages:")
packages_to_check = ["mujoco", "robosuite", "robomimic", "numpy", "scipy", "h5py", "torch", "PIL", "opencv"]
for pkg in packages_to_check:
    try:
        mod = __import__(pkg)
        version = getattr(mod, "__version__", "unknown")
        print(f"  [OK] {pkg}: {version}")
    except ImportError:
        print(f"  [MISSING] {pkg}")

# 3. 安装 mujoco
print("\n[3] Installing mujoco:")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "mujoco==3.10.0", "--quiet"],
    capture_output=True, text=True, timeout=300
)
print(f"  stdout: {result.stdout[-500:] if result.stdout else ''}")
print(f"  stderr: {result.stderr[-500:] if result.stderr else ''}")
print(f"  returncode: {result.returncode}")

# 4. 安装其他依赖
print("\n[4] Installing other dependencies:")
other_deps = ["Pillow", "opencv-python", "h5py", "imageio"]
for dep in other_deps:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", dep, "--quiet"],
        capture_output=True, text=True, timeout=180
    )
    status = "OK" if result.returncode == 0 else "FAIL"
    print(f"  [{status}] {dep} (rc={result.returncode})")

# 5. 设置环境变量
print("\n[5] Setting environment variables:")
os.environ["MUJOCO_GL"] = "egl"
os.environ["PYOPENGL_PLATFORM"] = "egl"
print(f"  MUJOCO_GL={os.environ.get('MUJOCO_GL')}")
print(f"  PYOPENGL_PLATFORM={os.environ.get('PYOPENGL_PLATFORM')}")

# 6. 验证 mujoco 安装
print("\n[6] Verifying mujoco:")
try:
    import mujoco
    print(f"  [OK] mujoco version: {mujoco.__version__}")
    # 测试 viewer 模块
    try:
        from mujoco import viewer
        print(f"  [OK] mujoco.viewer imported")
    except ImportError as e:
        print(f"  [WARN] mujoco.viewer import failed: {e}")
        # viewer 可能在 headless 模式下不可用，但 robosuite 需要它
        # 创建一个 mock viewer 模块
        print(f"  Creating mock mujoco.viewer module...")
except ImportError as e:
    print(f"  [FAIL] mujoco import failed: {e}")

# 7. 检查 EGL
print("\n[7] Checking EGL:")
try:
    import os
    os.environ["MUJOCO_GL"] = "egl"
    import mujoco
    # 创建一个简单的 model 测试渲染
    xml = "<mujoco><worldbody><light pos='0 0 3'/><geom type='sphere' size='0.5'/></worldbody></mujoco>"
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    renderer = mujoco.Renderer(model, 64, 64)
    mujoco.mj_forward(model, data)
    renderer.update_scene(data)
    img = renderer.render()
    print(f"  [OK] EGL rendering works, image shape: {img.shape}")
except Exception as e:
    print(f"  [FAIL] EGL rendering failed: {e}")

print("\n" + "=" * 70)
print("[DONE]")
"""


async def main():
    dsw = DswRemote()
    await dsw.connect()
    print("\n[Stage 266] 安装环境依赖...")
    output = await dsw.execute_via_jupyter_api(REMOTE_SCRIPT, timeout=600)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())
