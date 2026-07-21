import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
code = (
    "import importlib, os, subprocess\n"
    "for m in ['mujoco','robosuite','robomimic','h5py','OpenGL','termcolor','matplotlib','imageio','tensorboard']:\n"
    "    try:\n"
    "        importlib.import_module(m); print(m,'OK')\n"
    "    except Exception as e:\n"
    "        print(m,'FAIL',repr(e)[:90])\n"
    "print('MUJOCO_GL=',os.environ.get('MUJOCO_GL'))\n"
    "r=subprocess.run(['ls','/usr/lib/x86_64-linux-gnu/libOSMesa.so.8'],capture_output=True,text=True)\n"
    "print('libOSMesa:', r.stdout.strip() or 'MISSING')\n"
    "print('python:', sys.executable)\n"
)
print(c.run_python(code, timeout=120))
