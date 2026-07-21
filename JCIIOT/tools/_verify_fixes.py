import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "# collect script h5py import\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "s=open(p).read()\n"
    "print('h5py imported in collect:', 'import h5py' in s)\n"
    "# controller fix\n"
    "c='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/controllers/parts/controller.py'\n"
    "cs=open(c).read()\n"
    "print('mj_fullM fixed:', 'mj_fullM(self.sim.model._model, self.sim.data._data, mass_matrix)' in cs)\n"
    "# git status on instance\n"
    "import subprocess\n"
    "r=subprocess.run(['git','-C','/mnt/workspace/JCIIOT_repo/JCIIOT','status','--short'],capture_output=True,text=True,timeout=60)\n"
    "print('GIT STATUS:'); print(r.stdout[:1500])\n"
)
print(d.Dswhub().run_python(code, timeout=90))
