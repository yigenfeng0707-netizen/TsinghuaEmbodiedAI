import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python(
"import subprocess,os\n"
"for cmd in ['which xvfb-run','which Xvfb','ls /usr/bin/Xvfb','apt list --installed 2>/dev/null | grep -i xvfb','echo DISPLAY=$DISPLAY']:\n"
"    p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)\n"
"    print('$',cmd); print(p.communicate()[0].decode()[:500])\n", timeout=60))
