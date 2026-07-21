import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print("==== task_config.json ====")
print(c.run_python("print(open('/mnt/workspace/JCIIOT_repo/JCIIOT/knowledge/task_config.json').read())", timeout=30))
