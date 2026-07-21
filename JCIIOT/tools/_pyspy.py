import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import subprocess
# try py-spy
r = subprocess.run("pip install py-spy -q 2>&1 | tail -1; py-spy dump --pid 18447 2>&1 | head -40", shell=True, capture_output=True, text=True, timeout=120)
print("PYSY:", r.stdout[-1500:])
print("ERR:", r.stderr[-400:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=150))
