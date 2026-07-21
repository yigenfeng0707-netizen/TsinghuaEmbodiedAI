import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
# upload a check script and run it as a file for clean scope
inner = (
    "import importlib, os, subprocess, sys\n"
    "mods = ['mujoco','robosuite','robomimic','h5py','OpenGL','termcolor','matplotlib','imageio','imageio_ffmpeg','tensorboard','tensorboardX','einops','filters','yaml','tqdm','psutil','glfw','xvfb']\n"
    "for m in mods:\n"
    "    try:\n"
    "        importlib.import_module(m); print(m,'OK')\n"
    "    except Exception as e:\n"
    "        print(m,'FAIL',repr(e)[:100])\n"
    "print('MUJOCO_GL=',os.environ.get('MUJOCO_GL'))\n"
    "print('python=',sys.executable, sys.version.split()[0])\n"
    "for lib in ['/usr/lib/x86_64-linux-gnu/libOSMesa.so.8','/usr/bin/Xvfb']:\n"
    "    r=subprocess.run(['ls','-la',lib],capture_output=True,text=True)\n"
    "    print(lib, '->', r.stdout.strip().split('/')[-1] if r.returncode==0 else 'MISSING')\n"
    "r=subprocess.run(['which','xvfb-run'],capture_output=True,text=True)\n"
    "print('xvfb-run:', r.stdout.strip() or 'MISSING')\n"
)
c.s.put(d.BASE+"/api/contents/_envcheck.py", json={"type":"file","format":"text","content":inner}, timeout=30)
launch = (
    "import subprocess,os\n"
    "env={**os.environ}\n"
    "p=subprocess.Popen(['python','/mnt/workspace/_envcheck.py'],stdout=open('/mnt/workspace/_envcheck.log','w'),stderr=subprocess.STDOUT,env=env)\n"
    "print('LAUNCHED',p.pid)\n"
)
print(c.run_python(launch, timeout=30))
