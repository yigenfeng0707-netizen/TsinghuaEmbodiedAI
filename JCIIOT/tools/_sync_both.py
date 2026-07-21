import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
files = [
    (r"D:\APPs\TsinghuaEmbodiedAI\JCIIOT\src\robot_agent\environments\robosuite_backend.py",
     "JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py"),
    (r"D:\APPs\TsinghuaEmbodiedAI\JCIIOT\robosuite\robosuite\environments\factory_sorting\load_factory_sorting_evalization.py",
     "JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py"),
]
for local, remote in files:
    content = open(local, encoding="utf-8").read()
    c.s.put(d.BASE+"/api/contents/"+remote,
            json={"type":"file","format":"text","content":content}, timeout=60)
    print("uploaded", remote.split("/")[-1], len(content), "bytes")
