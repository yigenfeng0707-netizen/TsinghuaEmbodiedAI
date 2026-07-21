import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
CODE = r'''
import re
root="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting"
import os
pat=re.compile(r"render_mode|glfw|Glfw|has_offscreen|create_viewer|MujocoPyRenderer|def make_eval_env|def run_factory_sorting|MujocoEnv\(|offscreen")
for dp,dn,fn in os.walk(root):
    for f in fn:
        if f.endswith(".py"):
            p=os.path.join(dp,f)
            try:
                t=open(p).read()
            except: continue
            for i,line in enumerate(t.splitlines(),1):
                if pat.search(line):
                    print(f"{p}:{i}: {line}")
'''
print(d.Dswhub().run_python(CODE, timeout=60))
