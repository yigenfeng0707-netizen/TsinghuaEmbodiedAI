import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print(c.run_python(
"import glob, os\n"
"hits = sorted(glob.glob('/mnt/workspace/JCIIOT_repo/JCIIOT/bc_trained_models/**/model_epoch_*.pth', recursive=True), reverse=True)\n"
"for h in hits[:10]:\n"
"    print(h, os.path.getsize(h))\n"
"print('---also robosuite dir---')\n"
"for h in sorted(glob.glob('/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/model_epoch_*.pth'), reverse=True)[:5]:\n"
"    print(h, os.path.getsize(h))\n", timeout=30))
