import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "s=open(p).read()\n"
    "i=s.find('def write_dataset')\n"
    "print(s[i:i+900])\n"
    "print('=== after actions write ===')\n"
    "j=s.find('create_dataset(\"actions\"')\n"
    "print(s[j-200:j+700])\n"
)
print(d.Dswhub().run_python(code, timeout=60))
