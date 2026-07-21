import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys\n"
    "pkgs='mujoco==3.10.0 termcolor matplotlib h5py'\n"
    "r=subprocess.run([sys.executable,'-m','pip','install',*pkgs.split()],capture_output=True,text=True,timeout=600)\n"
    "print('rc',r.returncode)\n"
    "print(r.stdout[-600:])\n"
    "print('ERR',r.stderr[-400:])\n"
)
print(d.Dswhub().run_python(code, timeout=650))
