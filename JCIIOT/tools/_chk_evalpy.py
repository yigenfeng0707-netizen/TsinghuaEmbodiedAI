import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os, subprocess\n"
    "print('exists _eval.py:', os.path.exists('/mnt/workspace/_eval.py'))\n"
    "r=subprocess.run(['python','-c','import ast; ast.parse(open(\"/mnt/workspace/_eval.py\").read()); print(\"syntax ok\")'],capture_output=True,text=True,shell=False)\n"
    "print(r.stdout, r.stderr[-300:])\n"
)
print(d.Dswhub().run_python(code, timeout=60))
