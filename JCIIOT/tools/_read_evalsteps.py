import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py'\n"
    "s=open(p).read()\n"
    "for k in ['DEFAULT_EVAL_STEPS','eval_steps =','if args.eval_steps','args.eval_steps or','DEFAULT_POST_HOLD']:\n"
    "    for m in re.finditer(re.escape(k), s):\n"
    "        i=m.start(); print(k,'::',s[max(0,i-40):i+80].replace(chr(10),' ')); print()\n"
)
print(d.Dswhub().run_python(code, timeout=60))
