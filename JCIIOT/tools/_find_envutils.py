import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/utils/env_utils.py'\n"
    "src=open(p).read()\n"
    "for m in re.finditer(r'class \\w+', src): print(m.group(0))\n"
    "print('--- create_env_from_metadata caller in train.py ---')\n"
    "tp='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/scripts/train.py'\n"
    "t=open(tp).read()\n"
    "for m in re.finditer(r'EnvUtils', t): i=m.start(); print(t[max(0,i-40):i+60].replace(chr(10),' '))\n"
)
print(d.Dswhub().run_python(code, timeout=60))
