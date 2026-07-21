import sys, time
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
time.sleep(240)
code = (
    "import os, subprocess\n"
    "txt=open('/mnt/workspace/_eval.log').read()\n"
    "print('tail 1200:'); print(txt[-1200:])\n"
    "r=subprocess.run(\"pgrep -f load_factory_sorting_evalization\", shell=True, capture_output=True, text=True)\n"
    "print('pid:', r.stdout.strip() or 'DEAD')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
