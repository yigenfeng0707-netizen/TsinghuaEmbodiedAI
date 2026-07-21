import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "s=open(p).read()\n"
    "for k in ['--up-steps','--xy-steps','--down-steps','--settle-steps','--grasp-steps','--view-steps','--num-rollouts','--max-action','--demo-dir','--ep-path']:\n"
    "    m=re.search(re.escape(k)+r\"[^)]*?default=([^,\)]+)\", s, re.S)\n"
    "    if m: print(k,'default=',m.group(1).strip())\n"
    "    else: print(k,'NOT FOUND')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
