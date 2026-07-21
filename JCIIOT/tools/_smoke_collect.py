import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import os, subprocess, sys
os.environ["MUJOCO_GL"] = "osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
script = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
out = "/mnt/workspace/JCIIOT_repo/JCIIOT/demo_smoke_l1"
cmd = ["python", script, "--num-rollouts", "1", "--no-render", "--output-name", "demo_smoke_l1"]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=400)
print("RC", r.returncode)
print("OUT:", r.stdout[-1500:])
print("ERR:", r.stderr[-1500:])
# show produced hdf5
import glob, os
hits = glob.glob(out + "*")
print("ARTIFACTS:", hits)
for h in hits:
    if h.endswith(".hdf5"):
        import h5py
        with h5py.File(h, "r") as f:
            print("HDF5", h, "keys", list(f.keys())[:5], "demos", len(f.get("data", {})))
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_smoke_collect.py", json=payload, timeout=30)

code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa"}
r = subprocess.run(["python", "/mnt/workspace/_smoke_collect.py"], capture_output=True, text=True, timeout=450, env=env)
print("RC", r.returncode)
print(r.stdout[-2000:])
print("ERR:", r.stderr[-1000:])
'''
print(c.run_python(code, timeout=480))
