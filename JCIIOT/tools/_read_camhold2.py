import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "src=open(p).read()\n"
    "for fn in ['def camera_hold_part_action','def capture_camera_hold_targets','def optional_part_action']:\n"
    "    i=src.find(fn)\n"
    "    print('====',fn,'====')\n"
    "    print(src[i:i+700] if i>=0 else 'NOT FOUND'); print()\n"
)
print(d.Dswhub().run_python(code, timeout=60))
