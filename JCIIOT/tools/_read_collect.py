import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "src=open(p).read()\n"
    "print('LINES', len(src.splitlines()))\n"
    "for kw in ['action','_set_action','env.step','np.array','gripper','delta','eef','append','demo','obs']:\n"
    "    cnt=src.count(kw); print(kw, cnt)\n"
    "print('=== action-related snippets ===')\n"
    "for m in re.finditer(r'action|env.step|gripper_qpos|delta', src):\n"
    "    i=m.start(); seg=src[max(0,i-80):i+80].replace(chr(10),' ')\n"
    "    if 'action' in seg.lower() or 'step' in seg.lower(): print(repr(seg)); print()\n"
)
print(d.Dswhub().run_python(code, timeout=60))
