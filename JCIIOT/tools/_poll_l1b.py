import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,subprocess\n"
    "log='/mnt/workspace/_run_l1b.log'\n"
    "lines=open(log).read().splitlines()\n"
    "print('LINES',len(lines))\n"
    "print('\\n'.join(lines[-15:]))\n"
    "ps=subprocess.run('ps aux | grep _run_l1b | grep -v grep',shell=True,capture_output=True,text=True)\n"
    "print('PROC:', ps.stdout.strip()[:200] or 'not running')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
