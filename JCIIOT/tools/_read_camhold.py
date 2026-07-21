import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "src=open(p).read()\n"
    "i=src.find('def camera_hold_part_action')\n"
    "print(src[i:i+900] if i>=0 else 'NOT FOUND')\n"
    "print('=== camera_hold usages ===')\n"
    "for m in re.finditer(r'camera_hold|head|set_attachment|move_camera|camera', src):\n"
    "    j=m.start(); seg=src[max(0,j-30):j+60].replace(chr(10),' ')\n"
    "    if 'hold' in seg.lower() or 'camera' in seg.lower(): print(seg); print()\n"
)
print(d.Dswhub().run_python(code, timeout=60))
