import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, sys, subprocess
# inspect what GL backends THIS mujoco build accepts
for k in list(sys.modules):
    if k.startswith("mujoco"):
        del sys.modules[k]
import mujoco.rendering.classic.gl_context as gc
print("VALID MUJOCO_GL:", gc._VALID_MUJOCO_GL)
print("MUJOCO_GL env currently:", os.environ.get("MUJOCO_GL"))
# pip available versions
rc = subprocess.run("pip index versions mujoco 2>&1 | head -5", shell=True, capture_output=True, text=True)
print("pip versions:", rc.stdout.strip()[:300])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=90))
