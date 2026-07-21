import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os, glob, h5py, subprocess\n"
    "# full tail of collect20 log\n"
    "txt = open('/mnt/workspace/_collect20.log').read()\n"
    "print('=== FULL TAIL (last 1200) ===')\n"
    "print(txt[-1200:])\n"
    "# count demos in produced hdf5\n"
    "hits = glob.glob('/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/*/l1_20_*.hdf5')\n"
    "print('HDF5:', hits)\n"
    "if hits:\n"
    "    with h5py.File(hits[0],'r') as f:\n"
    "        demos = list(f['data'].keys())\n"
    "        print('num demos:', len(demos))\n"
    "# live collect pids\n"
    "r = subprocess.run(\"pgrep -af load_factory_sorting_1_3fo3erfhisem_collect\", shell=True, capture_output=True, text=True)\n"
    "print('LIVE:', r.stdout.strip() or 'none')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
