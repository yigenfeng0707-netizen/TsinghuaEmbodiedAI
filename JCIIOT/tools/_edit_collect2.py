import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''p="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
s=open(p).read()
# revert torso hold (needed for reach), keep head hold disabled (camera static)
s=s.replace('torso_action = None  # DISABLED for image-domain match', 'torso_action = camera_hold_part_action(robot, "torso")')
open(p,"w").write(s)
print("torso reverted:", 'torso_action = camera_hold_part_action(robot, "torso")' in s)
print("head still disabled:", 'head_action = None  # DISABLED' in s)
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_edit_collect2.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_edit_collect2.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout); print('ERR',r.stderr[-300:])", timeout=90))
