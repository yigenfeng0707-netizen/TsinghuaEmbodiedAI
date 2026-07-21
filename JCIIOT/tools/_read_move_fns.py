import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os
p = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
t = open(p).read()
import re
for fn in ["def step_towards_targets", "def move_vertically_below_sites", "def move_along_linear_segment"]:
    i = t.find(fn)
    print("====", fn, "====")
    print(t[i: i+1400])
    print()
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
