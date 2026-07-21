import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import json\n"
    "cfg=json.load(open('/mnt/workspace/JCIIOT_repo/JCIIOT/bc_l1_config.json'))\n"
    "print('encoder:', json.dumps(cfg['observation']['encoder'], indent=1)[:2000])\n"
)
print(d.Dswhub().run_python(code, timeout=60))
