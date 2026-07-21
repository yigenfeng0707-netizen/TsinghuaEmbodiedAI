import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import h5py, numpy as np
p="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5"
f=h5py.File(p,"r")
d=f["data"]
k=list(d.keys())[0]
demo=d[k]
states=demo["states"][:]
print("states shape:", states.shape)
print("first state[:20]:", states[0][:20])
# env info
env_meta=d.attrs.get("env_metadata",{}) if hasattr(d.attrs,"get") else d.attrs
print("attrs:", dict(d.attrs) if len(d.attrs)<20 else list(d.attrs.keys()))
# Also check if there are joint names stored
print("demo attrs:", dict(demo.attrs) if len(demo.attrs)<20 else list(demo.attrs.keys()))
# print initial eef pos from states vs obs
obs=demo["obs"]
print("obs right_eef_pos[0]:", obs["robot0_right_eef_pos"][0])
print("obs right_eef_pos[-1]:", obs["robot0_right_eef_pos"][-1])
print("states[0] full:", states[0])
f.close()
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_democheck2.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_democheck2.py'],stdout=open('/mnt/workspace/_democheck2.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))
