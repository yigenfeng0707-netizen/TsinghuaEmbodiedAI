import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

local = r"D:\APPs\TsinghuaEmbodiedAI\JCIIOT\src\robot_agent\workflows\champion_transport.py"
content = open(local, encoding="utf-8").read()
c = d.Dswhub()
# upload to instance workflows dir
dst = "/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/workflows/champion_transport.py"
c.s.put(d.BASE + "/api/contents/champion_transport.py", json={"type":"file","format":"text","content":content}, timeout=30)
# move it into place via a kernel command (Jupyter contents PUT writes to cwd; need absolute path)
code = (
    "import shutil, os\n"
    "src='/mnt/workspace/JCIIOT_repo/JCIIOT/champion_transport.py'\n"
    "dst='/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/workflows/champion_transport.py'\n"
    "os.makedirs(os.path.dirname(dst), exist_ok=True)\n"
    "shutil.move(src, dst)\n"
    "print('moved ->', dst, os.path.getsize(dst))\n"
)
print(c.run_python(code, timeout=60))
