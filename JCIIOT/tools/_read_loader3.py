import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "base='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py'\n"
    "t=open(base).read()\n"
    "import re\n"
    "for pat in ['file_manager','policy_factory','config_factory','load_model_metadata','def load_factory_sorting_policy','def make_eval_env','def run_rollout','RolloutRunner','get_action']:\n"
    "    m=re.search(re.escape(pat), t)\n"
    "    if m:\n"
    "        s=max(0,m.start()-80); e=min(len(t),m.start()+700)\n"
    "        print('==== '+pat+' ===='); print(t[s:e]); print()\n"
)
print(d.Dswhub().run_python(code, timeout=60))
