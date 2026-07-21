import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

# Write a .pth file to dist-packages so the repo is always importable
code = r'''
import os
pth = "/usr/local/lib/python3.12/dist-packages/jciiot_repo.pth"
with open(pth, "w") as f:
    f.write("/mnt/workspace/JCIIOT_repo/JCIIOT\n")
print("wrote", pth)
# verify
import subprocess
r = subprocess.run("python -c \"import robomimic, robosuite; print('OK', robosuite.__version__, 'robomimic', getattr(robomimic,'__version__','?'))\" 2>&1", shell=True, capture_output=True, text=True, timeout=60)
print("verify RC", r.returncode, r.stdout[-300:], r.stderr[-300:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=90))
