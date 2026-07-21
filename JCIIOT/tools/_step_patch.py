import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

# 1) kill current
kill = "import subprocess\nsubprocess.run('pkill -9 -f collect50b.py; pkill -9 -f load_factory_sorting_1_3fo3erfhisem_collect', shell=True)\nprint('killed')\n"
c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_k.py", json={"type":"file","format":"text","content":kill}, timeout=30)
print(c.run_python("import subprocess,os,time\nsubprocess.run(['python','/mnt/workspace/_k.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); time.sleep(3); print('done kill')", timeout=90))

# 2) patch step counts in collect script (halve interpolation steps -> faster, still valid grasp traj)
patch = r'''
import os
p = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
t = open(p).read()
repls = [
    ("DEFAULT_UP_STEPS = 60", "DEFAULT_UP_STEPS = 30"),
    ("DEFAULT_XY_STEPS = 120", "DEFAULT_XY_STEPS = 60"),
    ("DEFAULT_DOWN_STEPS = 80", "DEFAULT_DOWN_STEPS = 40"),
    ("DEFAULT_SETTLE_STEPS = 80", "DEFAULT_SETTLE_STEPS = 40"),
    ("DEFAULT_GRASP_STEPS = 40", "DEFAULT_GRASP_STEPS = 25"),
    ("DEFAULT_INITIAL_VIEW_STEPS = 30", "DEFAULT_INITIAL_VIEW_STEPS = 15"),
]
for a,b in repls:
    assert a in t, a
    t = t.replace(a,b)
open(p,"w").write(t)
print("patched step counts (halved)")
'''
c.s.put(d.BASE + "/api/contents/_patch_steps.py", json={"type":"file","format":"text","content":patch}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_patch_steps.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout[-200:], r.stderr[-200:])", timeout=90))
