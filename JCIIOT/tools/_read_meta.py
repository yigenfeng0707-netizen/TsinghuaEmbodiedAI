import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/utils/env_utils.py'\n"
    "src=open(p).read()\n"
    "i=src.find('def get_env_metadata_from_dataset')\n"
    "print(src[i:i+1600])\n"
)
print(d.Dswhub().run_python(code, timeout=60))
