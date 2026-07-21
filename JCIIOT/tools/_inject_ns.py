import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import h5py, glob
base="/mnt/workspace/JCIIOT_repo/JCIIOT"
hits=glob.glob(base+"/robosuite/robosuite/models/assets/demonstrations_private/*/l1_20_*.hdf5")
h=hits[0]
print("hdf5:", h)
f=h5py.File(h,"a")
added=0
for ep in f["data"].keys():
    g=f["data/"+ep]
    if "num_samples" not in g.attrs:
        ns=g["actions"].shape[0]
        g.attrs["num_samples"]=ns
        added+=1
f.attrs["total"]=sum(int(f["data/"+ep].attrs["num_samples"]) for ep in f["data"].keys())
f.close()
print("added num_samples to", added, "demos")
print("data.attrs total set")
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_inject_ns.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_inject_ns.py'],capture_output=True,text=True,timeout=120,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout); print('ERR',r.stderr[-300:])", timeout=150))
