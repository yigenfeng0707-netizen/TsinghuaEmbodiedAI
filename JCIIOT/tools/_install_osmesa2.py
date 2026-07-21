import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, sys, subprocess
# refresh apt and install osmesa + glu
print(subprocess.run("apt-get update 2>&1 | tail -3", shell=True, capture_output=True, text=True, timeout=300).stdout[-300:])
rc = subprocess.run("apt-get install -y libosmesa6 libglu1-mesa-dev 2>&1 | tail -6", shell=True, capture_output=True, text=True, timeout=400)
print("apt rc", rc.returncode, rc.stdout[-400:])
print("osmesa:", subprocess.run("ldconfig -p | grep -i osmesa", shell=True, capture_output=True, text=True).stdout.strip())
# PyOpenGL for osmesa python bindings
rc = subprocess.run("pip install PyOpenGL --no-deps 2>&1 | tail -3", shell=True, capture_output=True, text=True, timeout=200)
print("PyOpenGL rc", rc.returncode, rc.stdout[-200:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=600))
