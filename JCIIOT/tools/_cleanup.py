import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c=d.Dswhub()
for f in ["_bisect.py","_bisect2.py","_bisect3.py","_bisect4.py","_bisect5.py","_bisect6.py","_bisect7.py","_bisect8.py","_bisect9.py","_bisect10.py","_bisect11.py","_flowtest.py","_grasptest.py","_grasptest2.py","_xvfb_test.py"]:
    try:
        c.s.delete(d.BASE+"/api/contents/"+f)
        print("deleted", f)
    except Exception as e:
        print("skip", f, repr(e)[:80])
