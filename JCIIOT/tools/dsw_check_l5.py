"""检查 L5 轨迹帧数和 GIF 生成进程状态。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()
    code = r"""
import os, subprocess, json

# 1. 检查 L5 轨迹帧数
traj_dir = '/mnt/workspace/JCIIOT_repo/submission/trajectories'
for f in sorted(os.listdir(traj_dir)):
    if f.startswith('L5_'):
        path = os.path.join(traj_dir, f)
        with open(path) as fp:
            data = json.load(fp)
        frames = data.get('frames', [])
        print(f'L5 trajectory: {f}')
        print(f'  frames: {len(frames)}')
        print(f'  events: {len(data.get("events", []))}')
        break

# 2. 检查进程状态
print('\n=== Process status ===')
r = subprocess.run('ps aux | grep batch_generate_replay_gifs | grep -v grep', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout or '(not running)')

# 3. 检查 /tmp 磁盘空间
print('\n=== /tmp disk space ===')
r = subprocess.run('df -h /tmp', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)

# 4. 日志文件最后修改时间
log = '/tmp/gif_generation.log'
if os.path.exists(log):
    stat = os.stat(log)
    import time
    mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f'\nLog last modified: {mtime}')
    print(f'Current time: {now}')
    print(f'Log size: {stat.st_size} bytes')

# 5. 日志最后几行(完整)
print('\n=== Last 5 log lines ===')
r = subprocess.run('tail -5 /tmp/gif_generation.log', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)
"""
    print(d.run_python(code, timeout=30))


if __name__ == "__main__":
    main()
