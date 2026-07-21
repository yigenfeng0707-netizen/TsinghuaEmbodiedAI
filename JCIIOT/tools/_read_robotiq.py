import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print(c.run_python("print(open('/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/grippers/robotiq_gripper_140.xml').read()[:2500])", timeout=30))
