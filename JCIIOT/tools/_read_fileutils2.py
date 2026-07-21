import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "base='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/utils/file_utils.py'\n"
    "t=open(base).read()\n"
    "i=t.find('def get_env_metadata_from_dataset')\n"
    "print(t[i:i+900])\n"
    "j=t.find('def get_shape_metadata_from_dataset')\n"
    "print('=== shape_meta ===')\n"
    "print(t[j:j+1500])\n"
)
print(d.Dswhub().run_python(code, timeout=60))
