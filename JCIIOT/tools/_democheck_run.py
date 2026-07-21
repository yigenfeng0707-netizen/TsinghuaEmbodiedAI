import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import h5py, numpy as np, os
p="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5"
f=h5py.File(p,"r")
print("keys:", list(f.keys()))
d=f["data"]
print("num demos:", len(d))
# inspect first demo
k=list(d.keys())[0]
demo=d[k]
print("demo",k,"keys:", list(demo.keys()))
obs=demo["obs"]
print("obs keys:", list(obs.keys()))
# gripper z trajectory across all demos
for k in list(d.keys())[:5]:
    g=obs["robot0_right_eef_pos"][:] if "robot0_right_eef_pos" in obs else None
    gl=obs["robot0_left_eef_pos"][:] if "robot0_left_eef_pos" in obs else None
    if g is not None:
        print(f"{k}: right_eef z start={g[0,2]:.3f} end={g[-1,2]:.3f} min={g[:,2].min():.3f} max={g[:,2].max():.3f} steps={len(g)}")
    if gl is not None:
        print(f"{k}: left_eef  z start={gl[0,2]:.3f} end={gl[-1,2]:.3f} min={gl[:,2].min():.3f} max={gl[:,2].max():.3f}")
# object position
for ok in obs.keys():
    if "object" in ok.lower() or "crate" in ok.lower() or "container" in ok.lower():
        arr=obs[ok][:]
        print(f"  obs[{ok}] shape={arr.shape} sample={arr[0][:3]}")
# check actions
acts=demo["actions"][:]
print("actions shape:", acts.shape, "range:", acts.min(axis=0)[:3], acts.max(axis=0)[:3])
f.close()
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_democheck.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_democheck.py'],stdout=open('/mnt/workspace/_democheck.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))
