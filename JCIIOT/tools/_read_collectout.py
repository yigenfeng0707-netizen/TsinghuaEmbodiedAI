import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "s=open(p).read()\n"
    "for m in re.finditer(r'add_argument\\([^)]*\\)', s):\n"
    "    a=m.group(0)\n"
    "    if 'dir' in a.lower() or 'output' in a.lower() or 'path' in a.lower() or 'name' in a.lower(): print(a)\n"
)
print(d.Dswhub().run_python(code, timeout=60))
