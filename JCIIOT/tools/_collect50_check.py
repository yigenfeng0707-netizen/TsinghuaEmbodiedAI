import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, time
# wait a bit then show tail of collect log
time.sleep(20)
txt = open("/mnt/workspace/_collect50.log").read()
lines = txt.splitlines()
# show progress markers
prog = [l for l in lines if any(k in l for k in ["Attempts:","successes:","saved demos","Result:","rollout","RC=","Error","Traceback"])]
print("=== progress (last 15 markers) ===")
for l in prog[-15:]:
    print(l[:160])
print("=== tail ===")
print(txt[-800:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
