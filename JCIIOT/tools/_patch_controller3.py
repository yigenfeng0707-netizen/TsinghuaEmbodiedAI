import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os
p = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/controllers/parts/controller.py"
t = open(p).read()
print("BEFORE line227:", repr(t.splitlines()[226]))
old = "            mujoco.mj_fullM(self.sim.model._model, mass_matrix, self.sim.data.qM)"
new = "            mujoco.mj_fullM(self.sim.model._model, self.sim.data._data, mass_matrix)"
assert old in t, "exact old not found"
t = t.replace(old, new)
# also ensure mass_matrix is a clean zeros array
old2 = "            mass_matrix = np.ndarray(shape=(self.sim.model.nv, self.sim.model.nv), dtype=np.float64, order=\"C\")"
new2 = "            mass_matrix = np.zeros((self.sim.model.nv, self.sim.model.nv), dtype=np.float64, order=\"C\")"
if old2 in t:
    t = t.replace(old2, new2)
open(p, "w").write(t)
print("AFTER line227:", repr(open(p).read().splitlines()[226]))
print("PATCH APPLIED")
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
