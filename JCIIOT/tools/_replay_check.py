import sys, time
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
time.sleep(180)
code = (
    "import os, subprocess\n"
    "txt=open('/mnt/workspace/_replay.log').read()\n"
    "print('lines:', len(txt.splitlines()))\n"
    "print('tail 2000:'); print(txt[-2000:])\n"
    "r=subprocess.run(\"pgrep -f _replay.py\", shell=True, capture_output=True, text=True)\n"
    "print('pid:', r.stdout.strip() or 'DEAD')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
