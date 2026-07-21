import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys,os\n"
    "print('python:', sys.executable)\n"
    "print('conda env:', os.environ.get('CONDA_DEFAULT_ENV'))\n"
    "for pkg in ['termcolor','mujoco','robomimic','torch','numpy','PIL']:\n"
    "    r=subprocess.run([sys.executable,'-c',f'import {pkg}; print(\"{pkg}\", getattr({pkg},\"__version__\",\"?\"))'],capture_output=True,text=True)\n"
    "    print(pkg, 'OK' if r.returncode==0 else 'MISSING', r.stdout.strip() or r.stderr.strip()[:60])\n"
    "# pip list relevant\n"
    "r=subprocess.run([sys.executable,'-m','pip','list'],capture_output=True,text=True)\n"
    "print('termcolor in pip:', 'termcolor' in r.stdout)\n"
)
print(d.Dswhub().run_python(code, timeout=90))
