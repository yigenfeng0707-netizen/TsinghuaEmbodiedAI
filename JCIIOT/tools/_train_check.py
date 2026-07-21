import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
import time
_os.environ.pop("MUJOCO_GL", None)
time.sleep(180)
code = (
    "import os, subprocess\n"
    "txt=open('/mnt/workspace/_train.log').read()\n"
    "for k in ['Epoch','epoch','Train','loss','Error','Traceback','Exception','TRAIN_RC']:\n"
    "    pass\n"
    "print('lines:', len(txt.splitlines()))\n"
    "print('tail 1500:'); print(txt[-1500:])\n"
    "r=subprocess.run(\"pgrep -f robomimic/scripts/train.py\", shell=True, capture_output=True, text=True)\n"
    "print('pid:', r.stdout.strip() or 'DEAD')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
