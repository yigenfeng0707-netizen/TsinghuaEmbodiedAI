import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

SRC = "/mnt/workspace/JCIIOT_repo/JCIIOT/bc_trained_models/l1_run_v2/l1_bc_lordim_v2/20260718161523/models/model_epoch_300.pth"
DST = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/model_epoch_150.pth"

INNER = '''import os, shutil
src="__SRC__"; dst="__DST__"
if os.path.exists(dst):
    shutil.copy(dst, dst+".orig_bak")
print("dst exists before:", os.path.exists(dst))
shutil.copy(src, dst)
print("copied. dst size:", os.path.getsize(dst))
# verify loadable
import torch
ck=torch.load(dst, map_location="cpu", weights_only=False)
print("ckpt keys:", list(ck.keys())[:8])
print("has shape_metadata:", "shape_metadata" in ck)
'''
c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_copy_ckpt.py", json={"type":"file","format":"text","content":INNER.replace("__SRC__",SRC).replace("__DST__",DST)}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_copy_ckpt.py'],capture_output=True,text=True,timeout=120,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout[-800:]); print('ERR',r.stderr[-300:])", timeout=150))
