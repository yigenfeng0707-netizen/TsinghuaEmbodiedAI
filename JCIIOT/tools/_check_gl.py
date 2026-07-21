import sys
sys.path.insert(0, ".")
import tools.dswhub as d

code = r'''
import subprocess, importlib, os
def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr)[-800:]

# is mujoco importable now?
rc, out = run("python -c 'import mujoco; print(mujoco.__version__)' 2>&1 | tail -3")
print("MUJOCO:", rc, out)

# check osmesa / mesa libs
rc, out = run("ldconfig -p | grep -iE 'osmesa|GL.so|EGL' | head; dpkg -l | grep -iE 'mesa|osmesa' | head")
print("MESA LIBS:", rc, out)

# try osmesa backend
rc, out = run("MUJOCO_GL=osmesa python -c \"import mujoco,numpy as np; m=mujoco.MjModel.from_xml_string('<mujoco><worldbody><geom type=\\\"sphere\\\" size=\\\"0.1\\\"/></worldbody></mujoco>'); r=mujoco.Renderer(m,64,64); r.update_scene(mujoco.MjData(m)); r.render(); print('OSMESA RENDER OK')\" 2>&1 | tail -4")
print("OSMESA TEST:", rc, out)

# try egl again quickly
rc, out = run("MUJOCO_GL=egl python -c \"import mujoco,numpy as np; m=mujoco.MjModel.from_xml_string('<mujoco><worldbody><geom type=\\\"sphere\\\" size=\\\"0.1\\\"/></worldbody></mujoco>'); r=mujoco.Renderer(m,64,64); r.update_scene(mujoco.MjData(m)); r.render(); print('EGL RENDER OK')\" 2>&1 | tail -4")
print("EGL TEST:", rc, out)

# robosuite/robomimic importable?
rc, out = run("python -c 'import robosuite,robomimic; print(\"robosuite+robomimic OK\")' 2>&1 | tail -4")
print("ROBOSUITE/ROBOMIMIC:", rc, out)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=180))
