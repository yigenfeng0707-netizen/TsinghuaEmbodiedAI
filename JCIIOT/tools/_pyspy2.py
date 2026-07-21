import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import subprocess, os
# find the live collect pid
r = subprocess.run("pgrep -f load_factory_sorting_1_3fo3erfhisem_collect", shell=True, capture_output=True, text=True)
pid = r.stdout.strip().split("\n")[0]
print("live pid:", pid)
r2 = subprocess.run(f"py-spy dump --pid {pid} 2>&1 | head -20", shell=True, capture_output=True, text=True, timeout=120)
print(r2.stdout[-1200:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=150))
