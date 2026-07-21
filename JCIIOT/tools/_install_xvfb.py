import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python(
"import subprocess,os\n"
"print('--- whoami ---'); print(subprocess.run(['whoami'],capture_output=True,text=True).stdout)\n"
"print('--- apt-get install xvfb (may need sudo) ---')\n"
"p=subprocess.run('sudo apt-get update -qq && sudo apt-get install -y xvfb libxinerama1 libxcursor1 libxrandr2 libxinerama-dev 2>&1 | tail -20',shell=True,capture_output=True,text=True,timeout=300)\n"
"print(p.stdout[-1500:]); print('STDERR',p.stderr[-500:]); print('RC',p.returncode)\n", timeout=320))
