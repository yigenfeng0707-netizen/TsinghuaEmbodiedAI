import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python("import json; p='/mnt/workspace/JCIIOT_repo/JCIIOT/knowledge/robot_params.json'; d=json.load(open(p)); print('grasp_policy:', json.dumps(d.get('grasp_policy',{}), indent=2)); print('keys:', list(d.keys()))", timeout=60))
