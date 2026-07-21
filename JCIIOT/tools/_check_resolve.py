import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python(
"from pathlib import Path\n"
"f=Path('/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py')\n"
"root=f.resolve().parents[3]\n"
"print('PROJECT_ROOT=',root)\n"
"for cp in ['robosuite/robosuite/model_epoch_150.pth','robosuite/robosuite/model_epoch_500.pth']:\n"
"    p=(root/cp).resolve(); print(cp,'->',p,'EXISTS' if p.exists() else 'MISSING')\n", timeout=60))
