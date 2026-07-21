import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import h5py, json
h="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5"
raw=h5py.File(h,"r")["data"].attrs["env_args"]
print("raw type", type(raw), repr(raw)[:200])
s = raw.decode() if isinstance(raw,(bytes,str)) else str(raw)
ea=json.loads(s)
print("env_args:", ea)
print("lang in ea:", "lang" in ea)
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_chk.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_chk.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout); print('ERR',r.stderr[-300:])", timeout=90))
