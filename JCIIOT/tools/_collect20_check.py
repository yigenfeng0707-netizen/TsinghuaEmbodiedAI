import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
import time
_os.environ.pop("MUJOCO_GL", None)

time.sleep(720)
code = (
    "import os, subprocess\n"
    "txt=open('/mnt/workspace/_collect20.log').read()\n"
    "for k in ['Attempts:','successes:','saved demos','Result:','RC=']:\n"
    "    print(k, txt.count(k))\n"
    "r=subprocess.run(\"pgrep -f load_factory_sorting_1_3fo3erfhisem_collect\", shell=True, capture_output=True, text=True)\n"
    "print('pid:', r.stdout.strip() or 'DEAD')\n"
    "print('tail:', txt[-200:])\n"
)
print(d.Dswhub().run_python(code, timeout=60))
