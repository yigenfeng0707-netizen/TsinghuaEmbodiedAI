import sys
sys.path.insert(0, ".")
import tools.dswhub as d

code = r'''
import os
base = "/mnt/workspace/JCIIOT_repo/JCIIOT"
for n in ["requirements.txt", "robomimic/setup.py", "robosuite/requirements.txt", "robosuite/setup.py"]:
    p = os.path.join(base, n)
    print("==== " + n + " ====")
    try:
        print(open(p).read()[:1600])
    except Exception as e:
        print("ERR", e)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
