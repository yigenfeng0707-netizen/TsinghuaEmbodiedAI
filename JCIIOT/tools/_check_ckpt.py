import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python(
"import os\n"
"for f in ['/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/model_epoch_150.pth','/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/model_epoch_500.pth']:\n"
"    print(f, 'EXISTS' if os.path.exists(f) else 'MISSING', os.path.getsize(f) if os.path.exists(f) else 0)\n", timeout=60))
