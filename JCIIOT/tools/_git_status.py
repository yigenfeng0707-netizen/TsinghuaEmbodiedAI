import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess\n"
    "r=subprocess.run(['git','-C','/mnt/workspace/JCIIOT_repo/JCIIOT','status','--short'],capture_output=True,text=True,timeout=60)\n"
    "lines=[l for l in r.stdout.splitlines() if '__pycache__' not in l and '.pyc' not in l]\n"
    "print('NON-PYCACHE CHANGES:')\n"
    "print('\\n'.join(lines) if lines else '(none)')\n"
)
print(d.Dswhub().run_python(code, timeout=90))
