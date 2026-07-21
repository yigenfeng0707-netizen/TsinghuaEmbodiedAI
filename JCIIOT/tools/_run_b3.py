import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_run_b3.py", json={"type":"file","format":"text","content":
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_bisect3.py'],stdout=open('/mnt/workspace/_bisect3.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n"
}, timeout=30)
print(c.run_python(open("/dev/stdin").read() if False else "print('trigger')", timeout=10) if False else "ok")
print(c.run_python("print('x')", timeout=10))
