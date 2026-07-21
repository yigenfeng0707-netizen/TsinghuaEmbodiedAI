import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import h5py, glob, os
# the smoke demo
hits = glob.glob("/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/*/demo_smoke_l1_*.hdf5")
print("smoke hdf5:", hits)
if hits:
    with h5py.File(hits[0], "r") as f:
        print("top keys:", list(f.keys()))
        data = f["data"]
        print("num demos:", len(data))
        d0 = data["0"]
        print("demo0 keys:", list(d0.keys()))
        if "obs" in d0:
            print("obs keys:", list(d0["obs"].keys())[:10])
            for k in list(d0["obs"].keys())[:6]:
                print("  ", k, d0["obs"][k].shape, d0["obs"][k].dtype)
        if "actions" in d0:
            print("actions", d0["actions"].shape, d0["actions"].dtype)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
