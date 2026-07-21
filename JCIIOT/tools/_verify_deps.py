import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys\n"
    "for pkg in ['mujoco','termcolor','matplotlib','h5py']:\n"
    "    r=subprocess.run([sys.executable,'-c',f'import {pkg}; print(\"{pkg}\", getattr({pkg},\"__version__\",\"?\"))'],capture_output=True,text=True)\n"
    "    print(pkg, 'OK '+r.stdout.strip() if r.returncode==0 else 'MISSING')\n"
)
print(d.Dswhub().run_python(code, timeout=90))
