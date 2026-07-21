import sys, time
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
time.sleep(180)
code = (
    "import os, subprocess\n"
    "txt=open('/mnt/workspace/_collect1.log').read()\n"
    "print('collect tail:'); print(txt[-1200:])\n"
    "r=subprocess.run(\"pgrep -f load_factory_sorting_1_3fo3erfhisem_collect\", shell=True, capture_output=True, text=True)\n"
    "print('pid:', r.stdout.strip() or 'DEAD')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
