import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
code = (
"import json, numpy as np\n"
"APP='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
"cfg=json.load(open(APP+'/knowledge/task_config.json'))\n"
"# Update L2/L3/L5 to offset 0.8 (balance: not touching object + reachable)\n"
"updates={'L2':0.8, 'L3':0.8, 'L5':0.8}\n"
"for lvl,off in updates.items():\n"
"    pose=cfg['grasp_poses_by_level'][lvl]\n"
"    # recompute: base = grasp_mid + [off, -0.019]\n"
"    # grasp_mid from current: base - [old_off, -0.019]\n"
"    # easier: just shift x by (0.8 - old_off)\n"
"    old_off = pose['pos'][0] - (pose['pos'][0] - 0.019)  # not reliable, recompute below\n"
"print('skip, use direct recomputation')\n"
)
# Actually do it properly with site positions
print(c.run_python(code, timeout=30))
