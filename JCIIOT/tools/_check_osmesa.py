import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys,os,glob\n"
    "for pkg in ['OpenGL','pyopengl']:\n"
    "    r=subprocess.run([sys.executable,'-m','pip','show',pkg],capture_output=True,text=True)\n"
    "    print(pkg,'installed' if r.returncode==0 else 'NOT')\n"
    "# find libOSMesa\n"
    "found=[f for pat in ['/usr/lib/x86_64-linux-gnu/libOSMesa*','/usr/lib/libOSMesa*','/opt/rocm/*/libOSMesa*','/opt/rocm/lib/libOSMesa*'] for f in glob.glob(pat)]\n"
    "print('libOSMesa:', found[:5] or 'NONE')\n"
    "# dpkg\n"
    "r=subprocess.run('ldconfig -p | grep -i osmesa',shell=True,capture_output=True,text=True); print('ldconfig osmesa:', r.stdout.strip() or 'none')\n"
    "r=subprocess.run('dpkg -l | grep -i osmesa',shell=True,capture_output=True,text=True); print('dpkg osmesa:', r.stdout.strip() or 'none')\n"
    "r=subprocess.run('apt list --installed 2>/dev/null | grep -i mesa',shell=True,capture_output=True,text=True); print('apt mesa:', r.stdout[:300] or 'none')\n"
)
print(d.Dswhub().run_python(code, timeout=90))
