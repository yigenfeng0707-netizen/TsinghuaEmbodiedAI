import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print(c.run_python(
"import os\n"
"p='/mnt/workspace/JCIIOT_repo/JCIIOT/bc_l1_config.json'\n"
"print('bc_l1_config exists:', os.path.exists(p))\n"
"p2='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5'\n"
"print('demo hdf5 exists:', os.path.exists(p2), os.path.getsize(p2) if os.path.exists(p2) else 0)\n", timeout=30))
