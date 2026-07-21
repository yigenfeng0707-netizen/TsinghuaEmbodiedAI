import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python(
"import sys; APP='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
"for p in [APP+'/src',APP,APP+'/robomimic',APP+'/robosuite/robosuite']: sys.path.insert(0,p)\n"
"import importlib.util as u\n"
"spec=u.spec_from_file_location('rb','/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py')\n"
"rb=u.module_from_spec(spec); spec.loader.exec_module(rb)\n"
"rp=rb._load_robot_params()\n"
"print('grasp_policy:', rp.get('grasp_policy'))\n", timeout=60))
