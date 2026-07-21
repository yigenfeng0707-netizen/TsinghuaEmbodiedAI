import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys,os\n"
    "# install system libosmesa\n"
    "r=subprocess.run('apt-get update -qq',shell=True,capture_output=True,text=True,timeout=300)\n"
    "print('apt update rc',r.returncode, r.stderr[-200:])\n"
    "r=subprocess.run('apt-get install -y libosmesa6 libgl1-mesa-dev',shell=True,capture_output=True,text=True,timeout=400)\n"
    "print('apt install rc',r.returncode)\n"
    "print(r.stdout[-400:]); print('ERR',r.stderr[-400:])\n"
    "# verify libOSMesa now present\n"
    "r=subprocess.run('ldconfig -p | grep -i osmesa',shell=True,capture_output=True,text=True); print('osmesa now:', r.stdout.strip() or 'none')\n"
    "# install PyOpenGL\n"
    "r=subprocess.run([sys.executable,'-m','pip','install','PyOpenGL'],capture_output=True,text=True,timeout=300)\n"
    "print('pip PyOpenGL rc',r.returncode, r.stderr[-200:])\n"
)
print(d.Dswhub().run_python(code, timeout=800))
