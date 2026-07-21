import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print(c.run_python(
"import json\n"
"cfg=json.load(open('/mnt/workspace/JCIIOT_repo/JCIIOT/bc_l1_config.json'))\n"
"t=cfg.get('train',{})\n"
"for k in ['data','num_epochs','batch_size','learning_rate','data_format']:\n"
"    print(k,'=',t.get(k))\n"
"print('algo name=',cfg.get('algo',{}).get('name'))\n"
"print('experiment.name=',cfg.get('experiment',{}).get('name'))\n"
"print('experiment.validate=',cfg.get('experiment',{}).get('validate'))\n"
"print('experiment.save=',cfg.get('experiment',{}).get('save'))\n"
"print('experiment.epoch_rollback=',cfg.get('experiment',{}).get('epoch_rollback'))\n"
"print('experiment.rollout=',cfg.get('experiment',{}).get('rollout'))\n", timeout=30))
