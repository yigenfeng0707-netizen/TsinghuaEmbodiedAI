import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "base='/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py'\n"
    "t=open(base).read()\n"
    "import re\n"
    "for ln in [990, 1000, 1010, 1020, 1030, 1620, 1630, 1640, 1800, 1810, 1820, 1830]:\n"
    "    pass\n"
    "# print regions around BC usage\n"
    "for pat in ['BC_INPUT','model_epoch','robomimic','RolloutRunner','playback','policy','checkpoint','load_model','FileUtils']:\n"
    "    for m in re.finditer(pat, t):\n"
    "        s=max(0,m.start()-120); e=min(len(t),m.start()+200)\n"
    "        print('==== '+pat+' @'+str(m.start())+' ====')\n"
    "        print(t[s:e].replace(chr(10),' '))\n"
    "        print()\n"
    "        break  # first occurrence only, to keep output small\n"
)
print(d.Dswhub().run_python(code, timeout=60))
