import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys,os\n"
    "rm= '/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic'\n"
    "print('setup.py exists:', os.path.exists(rm+'/setup.py'))\n"
    "r=subprocess.run([sys.executable,'-m','pip','install','-e',rm,'--no-deps'],capture_output=True,text=True,timeout=600)\n"
    "print('rc',r.returncode)\n"
    "print(r.stdout[-500:]); print('ERR',r.stderr[-400:])\n"
)
print(d.Dswhub().run_python(code, timeout=650))
