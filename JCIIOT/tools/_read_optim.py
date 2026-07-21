import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import json\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/exps/templates/bc.json'\n"
    "cfg=json.load(open(p))\n"
    "print('optim_params:', json.dumps(cfg['algo']['optim_params'], indent=1)[:1500])\n"
    "print('algo keys:', list(cfg['algo'].keys()))\n"
)
print(d.Dswhub().run_python(code, timeout=60))
