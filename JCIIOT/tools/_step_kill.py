import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

# Step 1: ensure old procs dead
kill_script = (
    "import subprocess\n"
    "subprocess.run('pkill -9 -f collect50.py; pkill -9 -f load_factory_sorting_1_3fo3erfhisem_collect', shell=True)\n"
    "print('killed old')\n"
)
c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_k.py", json={"type":"file","format":"text","content":kill_script}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_k.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout[-200:]); import time; time.sleep(3); r2=subprocess.run(\"pgrep -af 'collect50.py|load_factory_sorting_1_3fo3erfhisem_collect'\",shell=True,capture_output=True,text=True); print('remaining:',r2.stdout.strip() or 'none')", timeout=90))
