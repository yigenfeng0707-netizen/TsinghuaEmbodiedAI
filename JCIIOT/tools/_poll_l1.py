import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,time\n"
    "log='/mnt/workspace/_run_l1b.log'\n"
    "if os.path.exists(log):\n"
    "    lines=open(log).read().splitlines()\n"
    "    print('LINES',len(lines))\n"
    "    print('\\n'.join(lines[-25:]))\n"
    "else:\n"
    "    print('no log yet')\n"
    "import subprocess\n"
    "ps=subprocess.run(['ps','-p','64318','-o','pid,etime,stat'],capture_output=True,text=True)\n"
    "print('PS:',ps.stdout.strip())\n"
)
print(d.Dswhub().run_python(code, timeout=60))
