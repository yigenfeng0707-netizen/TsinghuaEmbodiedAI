"""DSW 上测试 mujoco 渲染（GLFW + Xvfb）。"""
import os
import subprocess
import sys

# 1. 检查/安装 Xvfb
print("=== 1. Xvfb ===")
r = subprocess.run("which Xvfb || echo NO_XVFB", capture_output=True, text=True, shell=True)
xvfb = r.stdout.strip()
print(f"Xvfb: {xvfb}")

if xvfb == "NO_XVFB":
    print("Installing Xvfb...")
    r = subprocess.run("apt-get update -qq && apt-get install -y -qq xvfb 2>&1 | tail -3",
                       capture_output=True, text=True, shell=True, timeout=120)
    print(r.stdout)
    r = subprocess.run("which Xvfb", capture_output=True, text=True, shell=True)
    xvfb = r.stdout.strip()
    print(f"After install: {xvfb}")

# 2. 启动 Xvfb
print("\n=== 2. Start Xvfb ===")
os.environ["DISPLAY"] = ":99"
subprocess.run("pkill Xvfb 2>/dev/null; sleep 1", shell=True)
subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1024x768x24"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import time
time.sleep(2)
r = subprocess.run("ps aux | grep Xvfb | grep -v grep", capture_output=True, text=True, shell=True)
print(f"Xvfb running: {'yes' if r.stdout.strip() else 'no'}")

# 3. 测试 mujoco 渲染
print("\n=== 3. Test mujoco render ===")
os.environ["MUJOCO_GL"] = "glfw"

try:
    import mujoco
    from mujoco import Renderer
    print(f"mujoco {mujoco.__version__} imported OK")

    xml = '<mujoco><worldbody><light pos="0 0 3"/><geom type="sphere" size="0.5"/></worldbody></mujoco>'
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    renderer = Renderer(model, height=120, width=160)
    mujoco.mj_forward(model, data)
    renderer.update_scene(data)
    pixels = renderer.render()
    print(f"Render OK! shape={pixels.shape}, dtype={pixels.dtype}")

    # 保存测试图
    from PIL import Image
    Image.fromarray(pixels).save("/tmp/test_render.png")
    print("Saved /tmp/test_render.png")

except Exception as e:
    import traceback
    print(f"FAIL: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
