import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys\n"
    "for pkg in ['imageio','tensorboardX','einops','tqdm','psutil']:\n"
    "    r=subprocess.run([sys.executable,'-c',f'import {pkg}'],capture_output=True,text=True)\n"
    "    print(pkg, 'OK' if r.returncode==0 else 'MISSING')\n"
    "# re-test robomimic full import chain\n"
    "APP='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
    "env=dict(os.environ); env['PYTHONPATH']=APP+'/src'+':'+APP+':'+APP+'/robomimic'+':'+APP+'/robosuite/robosuite'\n"
    "r=subprocess.run([sys.executable,'-c','import robomimic; from robomimic.utils.file_utils import policy_from_checkpoint; print(\"robomimic chain OK\")'],capture_output=True,text=True,env=env)\n"
    "print('chain:', 'OK' if r.returncode==0 else 'FAIL', r.stderr.strip()[-300:])\n"
)
print(d.Dswhub().run_python(code, timeout=90))
