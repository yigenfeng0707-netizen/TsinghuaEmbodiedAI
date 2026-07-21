import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa"}
# full import error
r = subprocess.run("python -c \"import robomimic\" 2>&1", shell=True, capture_output=True, text=True, timeout=60, env=env)
print("STDOUT:", r.stdout[-400:])
print("STDERR:", r.stderr[-800:])
# where is the editable pth / egg-link
r2 = subprocess.run("find /usr/local/lib/python3.12/dist-packages -maxdepth 1 \\( -name '*robomimic*' -o -name '__editable__*robomimic*' \\) 2>/dev/null; pip show -f robomimic 2>&1 | head -20", shell=True, capture_output=True, text=True, timeout=60)
print("META:", r2.stdout[-800:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=120))
