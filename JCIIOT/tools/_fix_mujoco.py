import sys
sys.path.insert(0, ".")
import tools.dswhub as d

code = r'''
import subprocess, os
os.environ.pop("MUJOCO_GL", None)
def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=240, env={**os.environ, "MUJOCO_GL":""})
    return r.returncode, (r.stdout + r.stderr)[-600:]

# upgrade mujoco to a version that supports the 'mujoco' software GL backend (>=3.10)
rc, out = run("pip install 'mujoco>=3.10' --no-deps -q 2>&1 | tail -3")
print("UPGRADE MUJOCO:", rc, out)

# unset MUJOCO_GL and test software renderer
rc, out = run("python -c \"import mujoco,numpy as np; print('mj',mujoco.__version__); m=mujoco.MjModel.from_xml_string('<mujoco><worldbody><geom type=\\\"sphere\\\" size=\\\"0.1\\\"/></worldbody></mujoco>'); r=mujoco.Renderer(m,64,64); r.update_scene(mujoco.MjData(m)); r.render(); print('SW RENDER OK')\" 2>&1 | tail -5")
print("SW RENDER:", rc, out)

rc, out = run("python -c 'import robosuite,robomimic; print(\"robosuite\", robosuite.__version__, \"robomimic OK\")' 2>&1 | tail -4")
print("ROBOSUITE/ROBOMIMIC:", rc, out)
'''
c = d.Dswhub()
# ensure env clean for the kernel call
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(c.run_python(code, timeout=300))
