"""上传脚本到 DSW 并用 .venv python 执行。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def upload_and_run(d, local_path, remote_path, label="", timeout=120):
    """上传脚本并通过 .venv python 执行。"""
    content = Path(local_path).read_text(encoding="utf-8")

    # 上传
    import json
    upload_code = (
        "import os\n"
        f"path = {remote_path!r}\n"
        f"content = {json.dumps(content)}\n"
        "with open(path, 'w', encoding='utf-8') as f:\n"
        "    f.write(content)\n"
        "print(f'Uploaded {os.path.getsize(path)} bytes to {path}')\n"
    )
    d.run_python(upload_code, timeout=20)

    # 执行
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")

    run_code = (
        "import subprocess, os\n"
        "venv_python = '/mnt/workspace/JCIIOT_repo/.venv/bin/python'\n"
        f"script = {remote_path!r}\n"
        "repo = '/mnt/workspace/JCIIOT_repo'\n"
        "env = os.environ.copy()\n"
        "env['PYTHONPATH'] = ':'.join([\n"
        "    os.path.join(repo, 'JCIIOT', 'src'),\n"
        "    os.path.join(repo, 'JCIIOT', 'robosuite'),\n"
        "    os.path.join(repo, 'JCIIOT', 'robosuite', 'robosuite'),\n"
        "    os.path.join(repo, 'JCIIOT', 'robomimic'),\n"
        "    os.path.join(repo, 'JCIIOT'),\n"
        "])\n"
        "env['MUJOCO_GL'] = 'glfw'\n"
        "env['DISPLAY'] = ':99'\n"
        f"r = subprocess.run([venv_python, script], capture_output=True, text=True, env=env, timeout={timeout})\n"
        "print(r.stdout)\n"
        "if r.stderr:\n"
        "    print('STDERR:', r.stderr[:2000])\n"
        "print(f'EXIT: {r.returncode}')\n"
    )
    print(d.run_python(run_code, timeout=timeout + 30))


def main():
    d = Dswhub()

    # 上传并运行渲染测试
    upload_and_run(
        d,
        local_path=Path(__file__).parent / "dsw_render_test.py",
        remote_path="/mnt/workspace/JCIIOT_repo/JCIIOT/tools/dsw_render_test.py",
        label="Render Test (GLFW + Xvfb)",
        timeout=120
    )


if __name__ == "__main__":
    main()
