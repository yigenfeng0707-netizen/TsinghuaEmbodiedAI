"""在 DSW kernel 里执行 GIF 生成(输出到 /tmp 绕过 NAS 配额)。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    # 上传最新的 batch_generate_replay_gifs.py 到 /tmp(避开 NAS 配额)
    import json
    local_script = Path(__file__).parent / "batch_generate_replay_gifs.py"
    content = local_script.read_text(encoding="utf-8")
    upload_code = (
        "import os\n"
        "path = '/tmp/batch_generate_replay_gifs.py'\n"
        f"content = {json.dumps(content)}\n"
        "with open(path, 'w', encoding='utf-8') as f:\n"
        "    f.write(content)\n"
        "print(f'Uploaded {os.path.getsize(path)} bytes to ' + path)\n"
    )
    print("Uploading script to /tmp...")
    print(d.run_python(upload_code, timeout=20))

    # 在 kernel 里设置环境并执行 GIF 生成
    code = r"""
import os, subprocess, time

# 1. 确保 Xvfb 运行
os.environ['DISPLAY'] = ':99'
r = subprocess.run('ps aux | grep "[X]vfb" | head -1', capture_output=True, text=True, shell=True)
if not r.stdout.strip():
    subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    print('Xvfb started')
else:
    print('Xvfb already running')

# 2. 设置环境
repo = '/mnt/workspace/JCIIOT_repo'
env = os.environ.copy()
env['MUJOCO_GL'] = 'glx'  # glx 跳过 macros 强制 EGL,走 GLFWGLContext+Xvfb
env['DISPLAY'] = ':99'
env['PYTHONPATH'] = ':'.join([
    os.path.join(repo, 'JCIIOT', 'src'),
    os.path.join(repo, 'JCIIOT', 'tools'),
    os.path.join(repo, 'JCIIOT', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robosuite', 'robosuite'),
    os.path.join(repo, 'JCIIOT', 'robomimic'),
    os.path.join(repo, 'JCIIOT'),
])
venv_python = os.path.join(repo, '.venv', 'bin', 'python')
traj_dir = os.path.join(repo, 'submission', 'trajectories')
# 输出到 /tmp(绕过 NAS 配额)
out_dir = '/tmp/replay_gifs'
log_file = '/tmp/gif_generation.log'
script_path = '/tmp/batch_generate_replay_gifs.py'

# 确保输出目录存在(在本地磁盘)
os.makedirs(out_dir, exist_ok=True)

# 3. 用 nohup 后台启动 GIF 生成
cmd = (
    f'cd /tmp && '
    f'MUJOCO_GL=glx DISPLAY=:99 '
    f'PYTHONPATH={env["PYTHONPATH"]} '
    f'{venv_python} {script_path} '
    f'--traj-dir {traj_dir} --out-dir {out_dir} '
    f'> {log_file} 2>&1'
)
print(f'Starting GIF generation...')
print(f'Log: {log_file}')
print(f'Out: {out_dir}')
print(f'Cmd: {cmd[:200]}...')

# 清理旧日志
with open(log_file, 'w') as f:
    f.write('')

# nohup 启动
subprocess.run(f'nohup bash -c {chr(39)}{cmd}{chr(39)} &', shell=True)
time.sleep(5)

# 读取初始日志
with open(log_file) as f:
    initial_log = f.read()
print('Initial log:')
print(initial_log if initial_log else '(waiting for output...)')
"""
    print("\n=== Starting GIF generation ===")
    print(d.run_python(code, timeout=60))

    # 轮询日志
    import time as _time
    for i in range(30):
        _time.sleep(15)
        poll_code = (
            "import os\n"
            "log = '/tmp/gif_generation.log'\n"
            "if os.path.exists(log):\n"
            "    with open(log) as f:\n"
            "        content = f.read()\n"
            "    print(content[-2000:])\n"
            "    if '完成' in content or 'EXIT' in content or 'Error' in content or 'FAIL' in content:\n"
            "        print('DONE_OR_ERROR')\n"
            "else:\n"
            "    print('LOG_NOT_EXISTS')\n"
        )
        result = d.run_python(poll_code, timeout=15)
        print(f"\n--- Poll {i+1}/30 ---")
        print(result)
        if "DONE_OR_ERROR" in result:
            break


if __name__ == "__main__":
    main()
