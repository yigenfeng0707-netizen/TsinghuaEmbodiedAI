import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, subprocess, glob
os.environ.pop("MUJOCO_GL", None)
# clean reinstall mujoco to a known-good version
subprocess.run("pip uninstall -y mujoco 2>&1 | tail -2", shell=True, capture_output=True, text=True)
# remove stale pycache
for p in glob.glob("/usr/local/lib/python3.12/dist-packages/mujoco/__pycache__"):
    subprocess.run(f"rm -rf {p}", shell=True)
rc = subprocess.run("pip install mujoco==3.10.0 --no-deps --force-reinstall 2>&1 | tail -4", shell=True, capture_output=True, text=True)
print("reinstall rc", rc.returncode, rc.stdout[-400:])
import mujoco
print("mj", mujoco.__version__, "Renderer?", hasattr(mujoco, "Renderer"))
m = mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type=\"sphere\" size=\"0.1\"/></worldbody></mujoco>")
d = mujoco.MjData(m)
os.environ["MUJOCO_GL"] = "mujoco"
r = mujoco.Renderer(m, 64, 64); r.update_scene(d); img = r.render()
print("SW RENDER OK", img.shape)
os.environ["MUJOCO_GL"] = "osmesa"
r2 = mujoco.Renderer(m, 64, 64); r2.update_scene(d); img2 = r2.render()
print("OSMESA RENDER OK", img2.shape)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=240))
