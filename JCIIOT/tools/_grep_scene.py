import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/factory_sorting_1_3fo3erfhisem.py'\n"
    "src=open(p).read()\n"
    "for m in re.finditer(r'robot_base_pos|13\\.5|base_pos|8\\.0|4\\.6|4\\.599', src):\n"
    "    i=m.start(); seg=src[max(0,i-60):i+90].replace(chr(10),' ')\n"
    "    print(repr(seg)); print()\n"
)
print(d.Dswhub().run_python(code, timeout=60))
