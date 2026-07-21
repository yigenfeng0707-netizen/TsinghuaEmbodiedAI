import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import h5py, glob\n"
    "hits = glob.glob('/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/*/l1_20_*.hdf5')\n"
    "h=hits[0]\n"
    "print('FILE', h)\n"
    "with h5py.File(h,'r') as f:\n"
    "    print('TOP ATTRS:', dict(f.attrs))\n"
    "    print('TOP GROUPS:', list(f.keys()))\n"
    "    if 'env_args' in f:\n"
    "        print('env_args:', dict(f['env_args'].attrs))\n"
    "    if 'mask' in f: print('mask present')\n"
    "    if 'target' in f: print('target present')\n"
    "    d0=f['data']['demo_1']\n"
    "    print('demo_1 groups:', list(d0.keys()))\n"
    "    if 'obs' in d0:\n"
    "        print('obs subkeys:', list(d0['obs'].keys()))\n"
    "        # check for object/robot0_eef keys\n"
    "        for k in list(d0['obs'].keys()):\n"
    "            if 'eef' in k or 'object' in k or 'gripper' in k: print('  obs',k, d0['obs'][k].shape)\n"
)
print(d.Dswhub().run_python(code, timeout=60))
