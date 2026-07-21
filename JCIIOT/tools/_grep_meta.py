import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/utils/env_utils.py'\n"
    "src=open(p).read()\n"
    "for kw in ['env_args','def get_env_meta','env_meta =','lang =']:\n"
    "    for m in re.finditer(re.escape(kw), src):\n"
    "        i=m.start(); print('@',kw,'::', src[max(0,i-60):i+100].replace(chr(10),' ')); print()\n"
)
print(d.Dswhub().run_python(code, timeout=60))
