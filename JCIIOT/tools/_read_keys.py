import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import json\n"
    "cfg=json.load(open('/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/exps/templates/bc.json'))\n"
    "print('TOP:', list(cfg.keys()))\n"
    "print('algo keys:', list(cfg['algo'].keys()))\n"
    "print('experiment keys:', list(cfg['experiment'].keys()))\n"
    "print('observation keys:', list(cfg['observation'].keys()))\n"
)
print(d.Dswhub().run_python(code, timeout=60))
