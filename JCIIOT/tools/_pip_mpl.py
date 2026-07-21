import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,os\n"
    "r=subprocess.run([os.sys.executable,'-m','pip','install','matplotlib','--no-input','-q'],capture_output=True,text=True,timeout=120)\n"
    "print('RC',r.returncode); print(r.stdout[-400:]); print('ERR',r.stderr[-400:])\n"
)
print(d.Dswhub().run_python(code, timeout=150))
