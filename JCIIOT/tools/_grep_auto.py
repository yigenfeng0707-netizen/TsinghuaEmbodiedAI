import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/utils/train_utils.py'\n"
    "import re\n"
    "src=open(p).read()\n"
    "for m in re.finditer('auto_remove_exp_dir', src): i=m.start(); print(src[max(0,i-60):i+60].replace(chr(10),' ')); print()\n"
)
print(d.Dswhub().run_python(code, timeout=60))
