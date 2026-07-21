import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys,os\n"
    "print('kernel python:', sys.executable)\n"
    "# Is there a venv in the repo or workspace?\n"
    "for v in ['/mnt/workspace/JCIIOT_repo/venv','/mnt/workspace/venv','/mnt/workspace/JCIIOT_repo/JCIIOT/venv']:\n"
    "    print(v, os.path.exists(v))\n"
    "# check if mujoco pip package installed anywhere via pip show\n"
    "for pkg in ['mujoco','robomimic','termcolor']:\n"
    "    r=subprocess.run([sys.executable,'-m','pip','show',pkg],capture_output=True,text=True)\n"
    "    print(pkg, 'installed' if r.returncode==0 else 'NOT')\n"
    "# try installing termcolor quickly\n"
    "r=subprocess.run([sys.executable,'-m','pip','install','termcolor'],capture_output=True,text=True,timeout=120)\n"
    "print('pip install termcolor rc', r.returncode, r.stdout[-200:], r.stderr[-200:])\n"
)
print(d.Dswhub().run_python(code, timeout=160))
