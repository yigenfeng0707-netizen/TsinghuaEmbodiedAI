import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import sys
sys.path.insert(0, "/mnt/workspace/JCIIOT_repo/JCIIOT")
from robomimic.utils import obs_utils as ObsUtils
print("BACKBONES:", list(ObsUtils.OBS_ENCODER_BACKBONES.keys()))
print("CORES:", list(ObsUtils.OBS_ENCODER_CORES.keys()))
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_chk3.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_chk3.py'],capture_output=True,text=True,timeout=90,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout); print('ERR',r.stderr[-400:])", timeout=120))
