import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
local = r"D:\APPs\TsinghuaEmbodiedAI\JCIIOT\src\robot_agent\environments\robosuite_backend.py"
content = open(local, encoding="utf-8").read()
c.s.put(d.BASE+"/api/contents/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py",
        json={"type":"file","format":"text","content":content}, timeout=60)
print("uploaded", len(content), "bytes")
