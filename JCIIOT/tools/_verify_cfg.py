import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import json\n"
    "cfg=json.load(open('/mnt/workspace/JCIIOT_repo/JCIIOT/bc_l1_config.json'))\n"
    "print('has lr key:', 'lr' in json.dumps(cfg))\n"
    "print('learning_rate.initial:', cfg['algo']['optim_params']['policy']['learning_rate']['initial'])\n"
    "print('loss:', cfg['algo'].get('loss'))\n"
    "print('experiment.validate:', cfg['experiment']['validate'])\n"
    "print('train.dataset_keys:', cfg['train']['dataset_keys'])\n"
)
print(d.Dswhub().run_python(code, timeout=60))
