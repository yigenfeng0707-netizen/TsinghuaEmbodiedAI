import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python("import os; print('exists:', os.path.exists('/mnt/workspace/_run_l1b.py'), os.path.getsize('/mnt/workspace/_run_l1b.py') if os.path.exists('/mnt/workspace/_run_l1b.py') else 0)", timeout=60))
