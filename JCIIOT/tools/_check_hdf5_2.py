import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import h5py, glob
hits = glob.glob("/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/*/demo_smoke_l1_*.hdf5")
print("hdf5:", hits)
with h5py.File(hits[0], "r") as f:
    def walk(name, obj):
        if isinstance(obj, h5py.Dataset):
            print("DATASET", name, obj.shape, obj.dtype)
        else:
            print("GROUP", name, "keys:", list(obj.keys())[:8])
    f.visititems(walk)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
