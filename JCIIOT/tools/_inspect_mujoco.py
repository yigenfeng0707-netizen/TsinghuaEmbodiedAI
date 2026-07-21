import sys
sys.path.insert(0, ".")
import tools.dswhub as d

code = r'''
import mujoco, os
p = os.path.dirname(mujoco.__file__)
print("MUJOCO PKG:", p)
init = open(os.path.join(p, "__init__.py")).read()
print("=== __init__ mentions of Renderer/viewer ===")
for line in init.splitlines():
    if "Renderer" in line or "viewer" in line or "__all__" in line:
        print(repr(line))
# check viewer.py for Renderer class
vp = os.path.join(p, "viewer.py")
vtxt = open(vp).read()
import re
for m in re.finditer(r"class (\w*Renderer\w*)", vtxt):
    print("viewer.py class:", m.group(1))
# does top-level export Renderer anywhere?
print("grep Renderer in __init__:", "Renderer" in init)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
