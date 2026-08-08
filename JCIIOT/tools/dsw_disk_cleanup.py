"""检查 GIF 生成结果:文件列表 + 完整日志。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()
    code = r"""
import os

# 1. 检查 GIF 文件
out_dir = '/tmp/replay_gifs'
if os.path.exists(out_dir):
    files = sorted(os.listdir(out_dir))
    print(f'=== GIF files in {out_dir}: {len(files)} ===')
    total_size = 0
    for f in files:
        size = os.path.getsize(os.path.join(out_dir, f))
        total_size += size
        print(f'  {f}: {size//1024}KB')
    print(f'Total: {total_size//1024}KB')
else:
    print(f'{out_dir} does not exist')

# 2. 日志尾部(看是否有 OK / FAIL)
print('\n=== Log tail ===')
log = '/tmp/gif_generation.log'
if os.path.exists(log):
    with open(log) as f:
        lines = f.readlines()
    # 过滤掉 __del__ 异常噪音,只看关键行
    key_lines = [l.rstrip() for l in lines if any(k in l for k in ['===', 'OK', 'FAIL', 'Error:', '完成', 'SKIP', 'EXISTS', 'FULL', 'GRASP', '[ERROR]'])]
    print(f'Total log lines: {len(lines)}, key lines: {len(key_lines)}')
    for l in key_lines[-30:]:
        print(l)
else:
    print('No log file')

# 3. 检查 GIF 生成进程是否还在运行
import subprocess
r = subprocess.run('pgrep -f batch_generate_replay_gifs | head -1', capture_output=True, text=True, shell=True, timeout=5)
print(f'\nGIF process running: {bool(r.stdout.strip())}')
"""
    print(d.run_python(code, timeout=30))


if __name__ == "__main__":
    main()
