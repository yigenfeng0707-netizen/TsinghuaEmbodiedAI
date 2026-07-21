import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
CODE = r'''
import re,os
roots=["/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite",
       "/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/robomimic",
       "/usr/local/lib/python3.12/dist-packages/robomimic",
       "/usr/local/lib/python3.12/dist-packages/robosuite"]
pat=re.compile(r"glfw\.init|glfw\.create_window|import glfw|from glfw|GlfwContext|MujocoPyRenderer|offscreen_context|MjRenderContext|create_offscreen|egl|osmesa|MUJOCO_GL")
seen=set()
for root in roots:
    if not os.path.isdir(root): continue
    for dp,dn,fn in os.walk(root):
        for f in fn:
            if not f.endswith(".py"): continue
            p=os.path.join(dp,f)
            try: t=open(p).read()
            except: continue
            for i,line in enumerate(t.splitlines(),1):
                if pat.search(line) and "factory_sorting" not in p.replace("\\","/"):
                    key=(p,i)
                    if key in seen: continue
                    seen.add(key)
                    print(f"{p}:{i}: {line}")
'''
print(d.Dswhub().run_python(CODE, timeout=60))
