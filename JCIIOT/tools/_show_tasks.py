import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print(c.run_python(
"import json\n"
"APP='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
"cfg=json.load(open(APP+'/knowledge/task_config.json'))\n"
"for t in cfg['tasks']:\n"
"    gp=cfg['grasp_poses'].get(t['source'],{})\n"
"    print(t['level'], t['env_name'][:20], 'src='+t['source'], 'tgt='+t['target'], 'obj='+t['object'][:25], 'pose='+str(gp.get('pos')), 'yaw='+str(gp.get('yaw')))\n", timeout=30))
