"""DSW 环境探查 + 项目上传 + 依赖安装 + GIF 生成 一体化执行器。"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def run(d, code, timeout=60, label=""):
    if label:
        print(f"\n{'='*60}\n{label}\n{'='*60}")
    out = d.run_python(code, timeout=timeout)
    print(out)
    return out


def main():
    d = Dswhub()

    # 1. 探查 DSW 文件系统
    run(d, r"""
import os
for base in ['/mnt/workspace', '/mnt/workspace/dswQinghua']:
    print(f'=== {base} ===')
    if os.path.exists(base):
        for f in sorted(os.listdir(base)):
            full = os.path.join(base, f)
            t = 'DIR' if os.path.isdir(full) else 'FILE'
            sz = os.path.getsize(full) if os.path.isfile(full) else ''
            print(f'  {t:4} {f}  {sz}')
    else:
        print('  NOT FOUND')
""", timeout=20, label="1. 探查 DSW 文件系统")

    # 2. 检查是否有 conda 环境可用
    run(d, r"""
import subprocess
r = subprocess.run('conda env list 2>/dev/null || echo NO_CONDA', capture_output=True, text=True, shell=True)
print(r.stdout)
r2 = subprocess.run('pip list 2>/dev/null | grep -iE "mujoco|robosuite|pillow|numpy|gym|mujoco-py"', capture_output=True, text=True, shell=True)
print('Relevant packages:')
print(r2.stdout or '(none found)')
""", timeout=30, label="2. 检查 conda 环境")


if __name__ == "__main__":
    main()
