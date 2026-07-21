import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "src=open(p).read()\n"
    "for kw in ['robot_base_pos','FactorySorting','factory_sorting','robosuite.make','env =','make_factory','env_name','use_siemens']:\n"
    "    for m in re.finditer(re.escape(kw), src):\n"
    "        i=m.start(); seg=src[max(0,i-70):i+90].replace(chr(10),' ')\n"
    "        print(kw,'::',seg); print()\n"
    "        break\n"
)
print(d.Dswhub().run_python(code, timeout=60))
