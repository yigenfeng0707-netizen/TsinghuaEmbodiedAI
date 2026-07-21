import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import h5py
h="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5"
f=h5py.File(h,"r")
print("top data attrs:", list(f["data"].attrs.keys()))
print("groups:", list(f["data"].keys())[:3], "...total", len(list(f["data"].keys())))
g=f["data/"+list(f["data"].keys())[0]]
print("demo attrs:", list(g.attrs.keys()))
print("datasets:", list(g.keys()))
print("actions shape:", g["actions"].shape)
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_chk2.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_chk2.py'],capture_output=True,text=True,timeout=90,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout); print('ERR',r.stderr[-300:])", timeout=120))
