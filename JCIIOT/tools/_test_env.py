import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import os, traceback
os.environ["MUJOCO_GL"]="osmesa"
os.environ.pop("HF_HUB_OFFLINE", None)
import sys
sys.path.insert(0, "/mnt/workspace/JCIIOT_repo/JCIIOT")
from robomimic.utils.file_utils import get_env_metadata_from_dataset
h="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5"
em=get_env_metadata_from_dataset(h, set_env_specific_obs_processors=False)
print("env_meta:", em)
print("lang in meta:", em.get("lang"))
from robomimic.utils.env_utils import EnvUtils
try:
    env=EnvUtils.create_env_from_metadata(env_meta=em, render=False, render_offscreen=False, use_image_obs=False)
    print("env.lang =", repr(env.lang))
except Exception as e:
    print("ERR building env:", repr(e)[:200])
    traceback.print_exc()
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_test_env.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_test_env.py'],capture_output=True,text=True,timeout=180,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout[-1500:]); print('ERR',r.stderr[-400:])", timeout=210))
