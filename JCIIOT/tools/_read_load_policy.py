import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "base='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py'\n"
    "t=open(base).read()\n"
    "i=t.find('def load_factory_sorting_policy')\n"
    "print(t[i:i+3000])\n"
    "# also find how policy is used (run step) - search 'policy(' and 'get_action' and 'obs'\n"
    "import re\n"
    "for pat in ['def make_eval_env','policy(','get_action','obs_to','np.concatenate','robot0_robotview','actions']:\n"
    "    m=re.search(pat, t[i+3000:])\n"
    "    if m:\n"
    "        s=i+3000+m.start()-150; print('----',pat,'----'); print(t[s:s+500].replace(chr(10),' '))\n"
)
print(d.Dswhub().run_python(code, timeout=60))
