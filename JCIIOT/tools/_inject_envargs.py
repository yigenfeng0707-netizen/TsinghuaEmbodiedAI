import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import robomimic.utils.env_utils as EU\n"
    "print('EnvType:', [e for e in dir(EU.EnvType) if not e.startswith('_')])\n"
    "print('ROBOMIMIC_ROBOSUITE_ENV_TYPE =', getattr(EU.EnvType,'ROBOMIMIC_ROBOSUITE_ENV_TYPE', 'NA'))\n"
    "# inject env_args into the 20-demo hdf5\n"
    "import h5py, json, glob\n"
    "hits=glob.glob('/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/*/l1_20_*.hdf5')\n"
    "h=hits[0]; print('inject into', h)\n"
    "env_args=json.dumps({'env_name':'FactorySorting1_3FO3ERFHISEM','type':1,'env_kwargs':{}})\n"
    "with h5py.File(h,'a') as f:\n"
    "    f['data'].attrs['env_args']=env_args\n"
    "    print('env_args set:', f['data'].attrs['env_args'])\n"
)
print(d.Dswhub().run_python(code, timeout=90))
