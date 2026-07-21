import sys
sys.path.insert(0, ".")
import tools.dswhub as d

code = r'''
import subprocess, os

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return r.stdout.strip() + r.stderr.strip()

base = "/mnt/workspace/JCIIOT_repo/JCIIOT"
print("=== JCIIOT top ===")
print(run(f"ls {base}"))
print("=== robosuite dir ===")
print(run(f"ls {base}/robosuite | head"))
print("=== robomimic dir ===")
print(run(f"ls {base}/robomimic | head"))
print("=== setup.py / pyproject present? ===")
print(run(f"ls {base}/robosuite/setup.py {base}/robosuite/pyproject.toml {base}/robomimic/setup.py {base}/robomimic/pyproject.toml 2>&1"))
print("=== repo git status / remote ===")
print(run(f"cd {base} && git remote -v && git log --oneline -3 && git status -s | head"))
print("=== mujoco pip available? torch already there ===")
print(run("python -c 'import torch; print(torch.__version__, torch.cuda.is_available())'"))
print("=== is there a venv intended? look for activate scripts ===")
print(run("find /mnt/workspace -maxdepth 3 -name 'activate' 2>/dev/null | head; find / -maxdepth 5 -name 'mujoco' -type d 2>/dev/null | head"))
print("=== requirements files in repo ===")
print(run(f"find {base} -maxdepth 2 -name 'requirements*.txt' -o -maxdepth 2 -name 'setup.py' 2>/dev/null | head"))
'''
c = d.Dswhub()
print(c.run_python(code, timeout=120))
