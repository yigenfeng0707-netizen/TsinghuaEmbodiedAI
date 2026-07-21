import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "s=open(p).read()\n"
    "for k in ['DEFAULT_CAMERA','--camera','camera_height','camera_width']:\n"
    "    m=re.search(k+r'\\s*=\\s*[\"\\']?([^\"\\'\\n,]+)', s)\n"
    "    print(k,'=', m.group(1).strip() if m else None)\n"
    "print('--- EVAL defaults ---')\n"
    "p2='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py'\n"
    "s2=open(p2).read()\n"
    "for k in ['DEFAULT_CAMERA','--camera','camera_height','camera_width','DEFAULT_CAMERA_HEIGHT','DEFAULT_CAMERA_WIDTH']:\n"
    "    m=re.search(k+r'\\s*=\\s*[\"\\']?([^\"\\'\\n,]+)', s2)\n"
    "    print(k,'=', m.group(1).strip() if m else None)\n"
)
print(d.Dswhub().run_python(code, timeout=60))
