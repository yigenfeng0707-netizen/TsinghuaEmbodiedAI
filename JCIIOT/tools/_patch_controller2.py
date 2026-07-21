import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os
p = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/controllers/parts/controller.py"
t = open(p).read()
old = '''            mass_matrix = np.zeros((self.sim.model.nv, self.sim.model.nv), dtype=np.float64, order="C")
            mujoco.mj_fullM(self.sim.model._model, mass_matrix, self.sim.data.qM)'''
new = '''            mass_matrix = np.zeros((self.sim.model.nv, self.sim.model.nv), dtype=np.float64, order="C")
            mujoco.mj_fullM(self.sim.model._model, self.sim.data._data, mass_matrix)'''
assert old in t, "old snippet not found!"
t = t.replace(old, new)
open(p, "w").write(t)
print("patched controller.py: mj_fullM arg order fixed (m, d, dst)")
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
