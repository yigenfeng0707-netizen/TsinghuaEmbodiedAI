import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import json\n"
    "cfg=json.load(open('/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/exps/templates/bc.json'))\n"
    "print('loss:', json.dumps(cfg['algo']['loss'], indent=1))\n"
    "print('train keys:', list(cfg['train'].keys()))\n"
)
print(d.Dswhub().run_python(code, timeout=60))
