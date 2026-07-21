import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess, os\n"
    "G='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
    "def sh(cmd):\n"
    "    r=subprocess.run(cmd, cwd=G, shell=True, capture_output=True, text=True, timeout=120)\n"
    "    return r.returncode, r.stdout[-600:], r.stderr[-400:]\n"
    "rc,out,err = sh('git add robosuite/robosuite/controllers/parts/controller.py robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py robosuite/robosuite/model_epoch_150.pth bc_l1_config.json')\n"
    "print('add rc',rc,out,err)\n"
    "rc,out,err = sh('git reset HEAD bc_trained_models nohup.out robomimic/robomimic.egg-info robomimic/setup.py 2>/dev/null; rm -f robosuite/robosuite/model_epoch_150.pth.orig_bak robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py.bak_camhold')\n"
    "print('cleanup rc',rc)\n"
    "rc,out,err = sh('git commit -m \"Add BC grasp policy: trained low-dim checkpoint + controller mj_fullM fix + demo HDF5 metadata injection\"')\n"
    "print('commit rc',rc); print(out); print('ERR',err)\n"
    "rc,out,err = sh('git log --oneline -3')\n"
    "print('LOG:'); print(out)\n"
)
print(d.Dswhub().run_python(code, timeout=180))
