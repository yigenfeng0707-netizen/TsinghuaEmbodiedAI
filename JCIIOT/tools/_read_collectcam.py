import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "src=open(p).read()\n"
    "for kw in ['camera','render_camera','camera_names','robot0_robotview','OBS_KEYS','_image','imshow','seg']:\n"
    "    hits=list(re.finditer(re.escape(kw), src))\n"
    "    if hits:\n"
    "        m=hits[0]; i=m.start(); print(kw,'::',src[max(0,i-50):i+90].replace(chr(10),' ')); print()\n"
)
print(d.Dswhub().run_python(code, timeout=60))
