import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import subprocess, os
# find all mj_fullM calls in robosuite
r = subprocess.run("grep -rn 'mj_fullM' /mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/ 2>/dev/null", shell=True, capture_output=True, text=True)
print("=== all mj_fullM calls ===")
print(r.stdout)
# show controller.py line 220-230
r2 = subprocess.run("sed -n '218,232p' /mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/controllers/parts/controller.py", shell=True, capture_output=True, text=True)
print("=== controller.py 218-232 ===")
print(r2.stdout)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
