import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
code = (
"import json\n"
"APP='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
"cfg=json.load(open(APP+'/knowledge/task_config.json'))\n"
"# All scenes only have output_1..output_4. Fix invalid targets.\n"
"valid={'output_1','output_2','output_3','output_4'}\n"
"for t in cfg['tasks']:\n"
"    if t['target'] not in valid:\n"
"        old=t['target']; t['target']='output_4'\n"
"        print('fixed', t['level'], old, '->', t['target'])\n"
"json.dump(cfg, open(APP+'/knowledge/task_config.json','w'), indent=2, ensure_ascii=False)\n"
"print('DONE')\n"
)
print(c.run_python(code, timeout=30))
