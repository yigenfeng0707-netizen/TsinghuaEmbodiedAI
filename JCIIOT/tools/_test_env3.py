import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import os, traceback
os.environ["MUJOCO_GL"]="osmesa"
import sys
sys.path.insert(0, "/mnt/workspace/JCIIOT_repo/JCIIOT")
from robomimic.utils import file_utils as FU, env_utils as EU
h="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5"
em=FU.get_env_metadata_from_dataset(h)
try:
    env=EU.create_env_from_metadata(env_meta=em, render=False, render_offscreen=True, use_image_obs=True)
    print("OK env.lang=", repr(env.lang))
except Exception as e:
    print("ERR:", repr(e)[:150])
    traceback.print_exc()
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_test_env.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_test_env.py'],capture_output=True,text=True,timeout=300,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout[-2000:]); print('ERR',r.stderr[-400:])", timeout=330))
