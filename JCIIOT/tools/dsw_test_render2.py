"""测试 DSW 上 mujoco GLFW 渲染（通过 Xvfb）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    # 用 run_in_terminal 跑 shell 命令，避免 Python 字符串转义问题
    # 步骤 1: 检查 Xvfb 并启动
    print("=== 1. 检查 Xvfb ===")
    term_id, out = d.run_in_terminal(
        "which Xvfb || (apt-get install -y xvfb 2>/dev/null && which Xvfb) || echo NO_XVFB",
        wait=15
    )
    print(f"Xvfb: {out}")

    # 步骤 2: 启动 Xvfb
    print("\n=== 2. 启动 Xvfb ===")
    term_id, out = d.run_in_terminal(
        "export DISPLAY=:99 && (Xvfb :99 -screen 0 1024x768x24 &) && sleep 2 && echo XVFB_OK",
        wait=8
    )
    print(out)

    # 步骤 3: 测试 mujoco 渲染
    print("\n=== 3. 测试 mujoco 渲染 ===")
    cmd = (
        "export DISPLAY=:99 && "
        "export MUJOCO_GL=glfw && "
        "export PYTHONPATH="
        "/mnt/workspace/JCIIOT_repo/JCIIOT/src:"
        "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite:"
        "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite:"
        "/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic:"
        "/mnt/workspace/JCIIOT_repo/JCIIOT && "
        "cd /mnt/workspace/JCIIOT_repo/JCIIOT && "
        "/mnt/workspace/JCIIOT_repo/.venv/bin/python -c '"
        "import os; "
        "print(f\"MUJOCO_GL={os.environ.get(chr(77)+chr(85)+chr(74)+chr(79)+chr(67)+chr(79)+chr(95)+chr(71)+chr(76))}\"); "
        "import mujoco; from mujoco import Renderer; "
        "print(\"mujoco+Renderer OK\"); "
        "xml=\"<mujoco><worldbody><light pos=\\\"0 0 3\\\"/><geom type=\\\"sphere\\\" size=\\\"0.5\\\"/></worldbody></mujoco>\"; "
        "m=mujoco.MjModel.from_xml_string(xml); d2=mujoco.MjData(m); "
        "r=Renderer(m,height=120,width=160); "
        "mujoco.mj_forward(m,d2); r.update_scene(d2); px=r.render(); "
        "print(f\"Render OK shape={px.shape}\")"
        "'"
    )
    term_id, out = d.run_in_terminal(cmd, wait=30)
    print(out)


if __name__ == "__main__":
    main()
