import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess, os, time\n"
    "r = subprocess.run('pkill -9 -f load_factory_sorting_1_3fo3erfhisem_collect; pkill -9 -f collect50b.py; pkill -9 -f collect50.py', shell=True, capture_output=True, text=True)\n"
    "print('kill rc', r.returncode)\n"
    "time.sleep(3)\n"
    "r2 = subprocess.run(\"pgrep -af 'load_factory_sorting_1_3fo3erfhisem_collect|collect50' | grep -v pgrep\", shell=True, capture_output=True, text=True)\n"
    "print('remaining:', r2.stdout.strip() or 'none')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
