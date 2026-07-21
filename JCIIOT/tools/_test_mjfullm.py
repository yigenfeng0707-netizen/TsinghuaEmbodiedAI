import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, numpy as np, mujoco
print("numpy", np.__version__, "mujoco", mujoco.__version__)
# load the actual env model minimally to test mj_fullM
# Build a tiny model
xml = "<mujoco><worldbody><body><geom type='sphere' size='0.1'/><joint/></body></worldbody></mujoco>"
m = mujoco.MjModel.from_xml_string(xml)
dd = mujoco.MjData(m)
mujoco.mj_forward(m, dd)
nv = m.nv
# try various dst creations
for name, dst in [
    ("ndarray", np.ndarray((nv,nv), dtype=np.float64, order="C")),
    ("zeros", np.zeros((nv,nv), dtype=np.float64, order="C")),
    ("empty", np.empty((nv,nv), dtype=np.float64, order="C")),
    ("ascontig", np.ascontiguousarray(np.zeros((nv,nv)), dtype=np.float64)),
]:
    try:
        mujoco.mj_fullM(m, dst, dd.qM)
        print(name, "OK")
    except Exception as e:
        print(name, "FAIL", str(e)[:120])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=90))
