import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import subprocess, os
# robomimic bc config template
r = subprocess.run("cat /mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/exps/templates/bc.json 2>/dev/null | head -60", shell=True, capture_output=True, text=True)
print("=== bc.json ===")
print(r.stdout or "MISSING")
# how collect script names/saves & whether it aggregates into one hdf5
p = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
t = open(p).read()
i = t.find("output-name")
print("=== around output-name / save ===")
import re
for m in re.finditer(r"(hdf5|\.hdf5|output_name|demo_dir|save)", t):
    s=max(0,m.start()-60); print("...", t[s:m.start()+120].replace(chr(10)," "))
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
