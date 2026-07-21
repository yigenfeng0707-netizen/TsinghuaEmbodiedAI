import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''p="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
s=open(p).read()
# 1) restore head hold (revert diagnostic disable)
s=s.replace('head_action = None  # DISABLED for image-domain match', 'head_action = camera_hold_part_action(robot, "head")')
# 2) inject num_samples per demo group (robomimic training requires it)
needle='ep_data_grp.create_dataset("actions", data=np.array(actions))'
add='ep_data_grp.create_dataset("actions", data=np.array(actions))\\n        ep_data_grp.attrs["num_samples"] = len(actions)'
assert needle in s, "actions-write needle not found"
s=s.replace(needle, add, 1)
# 3) inject data.attrs["total"] for safety
if 'f["data"].attrs["total"]' not in s:
    s=s.replace('grp.attrs["num_successful_demos"] = num_eps',
                'grp.attrs["num_successful_demos"] = num_eps\\n    f["data"].attrs["total"] = sum(int(ep.attrs.get("num_samples",0)) for ep in f["data"].values() if isinstance(ep, h5py.Group))')
open(p,"w").write(s)
print("head restored:", 'head_action = camera_hold_part_action(robot, "head")' in s)
print("num_samples injected:", 'ep_data_grp.attrs["num_samples"] = len(actions)' in s)
print("total injected:", 'f["data"].attrs["total"]' in s)
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_enhance_collect.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_enhance_collect.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout); print('ERR',r.stderr[-300:])", timeout=90))
