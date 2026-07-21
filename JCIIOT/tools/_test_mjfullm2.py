import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import numpy as np, mujoco
xml = "<mujoco><worldbody><body><geom type='sphere' size='0.1'/><joint/></body></worldbody></mujoco>"
m = mujoco.MjModel.from_xml_string(xml)
dd = mujoco.MjData(m)
mujoco.mj_forward(m, dd)
nv = m.nv
dst = np.zeros((nv,nv), dtype=np.float64, order="C")
# correct modern signature: mj_fullM(m, d, dst)
try:
    mujoco.mj_fullM(m, dd, dst)
    print("mj_fullM(m, d, dst) OK, diag:", np.diag(dst)[:3])
except Exception as e:
    print("FAIL", str(e)[:150])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
