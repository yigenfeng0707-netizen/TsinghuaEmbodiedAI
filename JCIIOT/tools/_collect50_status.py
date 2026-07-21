import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, subprocess, time
# is the collect process alive?
r = subprocess.run("ps -eo pid,etime,cmd | grep -E 'load_factory_sorting_1_3fo3erfhisem_collect|collect50' | grep -v grep", shell=True, capture_output=True, text=True)
print("PROC:", r.stdout.strip() or "NOT RUNNING")
# log age + size
st = os.stat("/mnt/workspace/_collect50.log")
print("log mtime age(s):", int(time.time()-st.st_mtime), "size:", st.st_size)
# count progress lines
txt = open("/mnt/workspace/_collect50.log").read()
for k in ["Attempts:","successes:","saved demos","rollout","Result:"]:
    print(k, "count:", txt.count(k))
print("--- last 400 chars ---")
print(txt[-400:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
