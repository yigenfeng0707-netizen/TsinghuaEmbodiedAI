import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c=d.Dswhub()
local=r"D:\APPs\TsinghuaEmbodiedAI\JCIIOT\src\robot_agent\environments\robosuite_backend.py"
content=open(local, encoding="utf-8").read()
c.s.put(d.BASE+"/api/contents/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py",
        json={"type":"file","format":"text","content":content}, timeout=60)
# verify
import base64
r=c.s.get(d.BASE+"/api/contents/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py").json()
remote=base64.b64decode(r["content"]).decode("utf-8")
print("uploaded len", len(content), "remote len", len(remote))
print("fallback present:", "checkpoint_fallback_path" in remote)
print("GL teardown present:", "_render_context_offscreen = None" in remote)
