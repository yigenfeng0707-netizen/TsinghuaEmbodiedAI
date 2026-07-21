"""
Stage 268: 降级 numpy 到 2.1.x（numba 兼容版本）+ 升级 numba
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dsw_remote import DswRemote


REMOTE_SCRIPT = r"""
import os, sys, subprocess

print("=" * 70)
print("STAGE 268: DOWNGRADE NUMPY FOR NUMBA COMPATIBILITY")
print("=" * 70)

# 1. 显示当前版本
print("\n[1] Current versions:")
result = subprocess.run([sys.executable, "-m", "pip", "show", "numpy", "numba"],
                        capture_output=True, text=True, timeout=30)
print(result.stdout)

# 2. 降级 numpy 到 2.1.3（最新 2.1.x，numba 兼容）
print("\n[2] Downgrading numpy to 2.1.3:")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "numpy==2.1.3", "--quiet"],
    capture_output=True, text=True, timeout=300
)
print(f"  rc={result.returncode}")
print(f"  stderr: {result.stderr[-500:] if result.stderr else ''}")

# 3. 升级 numba 到最新
print("\n[3] Upgrading numba:")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "--upgrade", "numba", "--quiet"],
    capture_output=True, text=True, timeout=300
)
print(f"  rc={result.returncode}")
print(f"  stderr: {result.stderr[-500:] if result.stderr else ''}")

# 4. 验证
print("\n[4] Verify versions:")
# 清除已导入的模块
for mod_name in list(sys.modules.keys()):
    if "numpy" in mod_name or "numba" in mod_name:
        del sys.modules[mod_name]

try:
    import numpy as np
    print(f"  [OK] numpy: {np.__version__}")
except Exception as e:
    print(f"  [FAIL] numpy: {e}")

try:
    import numba
    print(f"  [OK] numba: {numba.__version__}")
except Exception as e:
    print(f"  [FAIL] numba: {e}")

# 5. 测试 mujoco + robosuite 导入
print("\n[5] Test mujoco + robosuite import:")
os.environ["MUJOCO_GL"] = "egl"
os.environ["PYOPENGL_PLATFORM"] = "egl"

# 清除已导入的模块
for mod_name in list(sys.modules.keys()):
    if "mujoco" in mod_name or "robosuite" in mod_name or "OpenGL" in mod_name:
        del sys.modules[mod_name]

try:
    import mujoco
    print(f"  [OK] mujoco: {mujoco.__version__}")
except Exception as e:
    print(f"  [FAIL] mujoco: {e}")

# 测试 robosuite 导入
sys.path.insert(0, "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite")
try:
    import robosuite
    print(f"  [OK] robosuite imported")
except Exception as e:
    print(f"  [FAIL] robosuite: {e}")
    import traceback
    traceback.print_exc()

print("\n[DONE]")
"""


async def main():
    dsw = DswRemote()
    await dsw.connect()
    print("\n[Stage 268] 降级 numpy...")
    output = await dsw.execute_via_jupyter_api(REMOTE_SCRIPT, timeout=600)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())
