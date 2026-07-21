import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import h5py, json, glob
hits = glob.glob("/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/*/l1_20_*.hdf5")
h = hits[0]; print("inject into", h)
env_args = json.dumps({"env_name": "FactorySorting1_3FO3ERFHISEM", "type": 1, "env_kwargs": {}})
with h5py.File(h, "a") as f:
    f["data"].attrs["env_args"] = env_args
    print("env_args set:", f["data"].attrs["env_args"])
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_inject.py", json=payload, timeout=30)
code = (
    "import subprocess, os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa'}\n"
    "r=subprocess.run(['python','/mnt/workspace/_inject.py'],capture_output=True,text=True,timeout=120,env=env)\n"
    "print('RC',r.returncode); print(r.stdout[-500:]); print('ERR',r.stderr[-400:])\n"
)
print(c.run_python(code, timeout=150))
