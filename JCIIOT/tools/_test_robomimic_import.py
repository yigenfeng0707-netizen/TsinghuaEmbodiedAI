import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys\n"
    "APP='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
    "env=dict(os.environ); env['PYTHONPATH']=APP+'/src'+':'+APP+':'+APP+'/robomimic'+':'+APP+'/robosuite/robosuite'\n"
    "for mod in ['robomimic','robomimic.utils.file_utils','robomimic.utils.torch_utils','robomimic.utils.env_utils']:\n"
    "    r=subprocess.run([sys.executable,'-c',f'import {mod}; print(\"OK {mod}\")'],capture_output=True,text=True,env=env)\n"
    "    print(mod, 'OK' if r.returncode==0 else 'FAIL', r.stderr.strip()[-300:] or r.stdout.strip()[-200:])\n"
)
print(d.Dswhub().run_python(code, timeout=90))
