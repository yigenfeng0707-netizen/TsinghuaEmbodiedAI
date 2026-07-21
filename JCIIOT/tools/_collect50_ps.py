import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import subprocess
# CPU usage of the collect pid
r = subprocess.run("top -b -n 1 -p 18447 2>/dev/null | tail -5", shell=True, capture_output=True, text=True)
print("TOP:", r.stdout.strip() or r.stderr.strip()[:200])
# thread count / state
r2 = subprocess.run("cat /proc/18447/status 2>/dev/null | grep -E 'State|Threads|VmRSS'", shell=True, capture_output=True, text=True)
print("STATUS:", r2.stdout.strip())
# wchan (what syscall it's waiting on)
r3 = subprocess.run("cat /proc/18447/wchan 2>/dev/null", shell=True, capture_output=True, text=True)
print("WCHAN:", r3.stdout.strip())
r4 = subprocess.run("cat /proc/18447/task/*/wchan 2>/dev/null | sort | uniq -c", shell=True, capture_output=True, text=True)
print("THREAD WCHANS:", r4.stdout.strip())
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
