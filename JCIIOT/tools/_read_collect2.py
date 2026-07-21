import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os
p = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
t = open(p).read()
# print argparse / main section
idx = t.find("argparse")
print("=== argparse/main region ===")
print(t[idx-200: idx+1500] if idx>=0 else "NO argparse found")
# also find if __name__ == main
im = t.rfind("if __name__")
print("=== main ===")
print(t[im: im+1200] if im>=0 else "NO main")
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
