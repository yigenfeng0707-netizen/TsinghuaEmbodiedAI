import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import h5py, json
h="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5"
ea=json.loads(h5py.File(h,"r")["data"].attrs["env_args"][()])
print("env_args:", ea)
print("has lang:", "lang" in ea, "has env_kwargs.lang:", "lang" in ea.get("env_kwargs",{}))
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_chk.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_chk.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout); print('ERR',r.stderr[-300:])", timeout=90))
