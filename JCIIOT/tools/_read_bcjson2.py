import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import json\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/exps/templates/bc.json'\n"
    "cfg=json.load(open(p))\n"
    "tr=cfg['train']\n"
    "print('data:', tr['data'])\n"
    "print('action_keys:', tr.get('action_keys'))\n"
    "print('dataset_keys:', tr.get('dataset_keys'))\n"
    "print('hdf5_load_next_obs:', tr.get('hdf5_load_next_obs'))\n"
    "print('seq_length:', tr.get('seq_length'))\n"
    "print('frame_stack:', tr.get('frame_stack'))\n"
    "ex=cfg['experiment']\n"
    "print('experiment.env:', ex.get('env'))\n"
    "print('experiment.validate:', ex.get('validate'))\n"
    "al=cfg['algo']\n"
    "print('algo_name:', al.get('algo_name'))\n"
)
print(d.Dswhub().run_python(code, timeout=60))
