"""检查 DSW 磁盘/配额使用情况(聚焦 JCIIOT_repo,避免全盘 du 超时)。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()

    code = r"""
import os, subprocess

# 1. 用户配额(quota)
print('=== Quota ===')
r = subprocess.run('quota -s 2>&1 || echo NO_QUOTA_CMD', capture_output=True, text=True, shell=True, timeout=15)
print(r.stdout)

# 2. JCIIOT_repo 总大小
print('\n=== JCIIOT_repo size ===')
r = subprocess.run('du -sh /mnt/workspace/JCIIOT_repo/ 2>/dev/null', capture_output=True, text=True, shell=True, timeout=90)
print(r.stdout or '(timeout or empty)')

# 3. JCIIOT_repo 各子目录大小
print('\n=== JCIIOT_repo subdirs ===')
r = subprocess.run('du -sh /mnt/workspace/JCIIOT_repo/*/ 2>/dev/null | sort -rh | head -15', capture_output=True, text=True, shell=True, timeout=90)
print(r.stdout or '(timeout or empty)')

# 4. .venv / cache 大小(通常是大头)
print('\n=== .venv + cache ===')
r = subprocess.run('du -sh /mnt/workspace/JCIIOT_repo/.venv/ 2>/dev/null; du -sh /mnt/workspace/.cache 2>/dev/null; du -sh ~/.cache/pip 2>/dev/null', capture_output=True, text=True, shell=True, timeout=60)
print(r.stdout)

# 5. inode 使用(可能是 inode 配额超,不是空间)
print('\n=== Inode usage ===')
r = subprocess.run('df -i /mnt/workspace', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)

# 6. 已有 GIF 文件
print('\n=== replay_gifs dir ===')
r = subprocess.run('ls -lah /mnt/workspace/JCIIOT_repo/submission/replay_gifs/ 2>/dev/null || echo NO_DIR', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)

# 7. 写入测试(确认配额是否真的超了)
print('\n=== Write test (10MB) ===')
try:
    test_file = '/mnt/workspace/JCIIOT_repo/_quota_test.tmp'
    with open(test_file, 'wb') as f:
        f.write(b'0' * 10 * 1024 * 1024)  # 10MB
    os.remove(test_file)
    print('Write 10MB: OK - quota NOT exceeded')
except Exception as e:
    print(f'Write 10MB: FAIL - {e}')

# 8. 之前 GIF 生成日志尾部(看报错)
print('\n=== gif_generation.log tail ===')
r = subprocess.run('tail -25 /mnt/workspace/JCIIOT_repo/gif_generation.log 2>/dev/null || echo NO_LOG', capture_output=True, text=True, shell=True, timeout=10)
print(r.stdout)
"""
    print(d.run_python(code, timeout=240))


if __name__ == "__main__":
    main()
