import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess\n"
    "r=subprocess.run(['find','/mnt/workspace','-name','champion_transport.py'],capture_output=True,text=True,timeout=60)\n"
    "print(r.stdout)\n"
)
print(d.Dswhub().run_python(code, timeout=90))
