import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import re
p="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
s=open(p).read()
bak=p+".bak_camhold"
open(bak,"w").write(s)
s=s.replace('head_action = camera_hold_part_action(robot, "head")', 'head_action = None  # DISABLED for image-domain match')
s=s.replace('torso_action = camera_hold_part_action(robot, "torso")', 'torso_action = None  # DISABLED for image-domain match')
open(p,"w").write(s)
print("edited. head present:", 'head_action = None' in s, "torso present:", 'torso_action = None' in s)
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_edit_collect.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_edit_collect.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout); print('ERR',r.stderr[-300:])", timeout=90))
