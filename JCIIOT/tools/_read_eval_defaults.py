import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py'\n"
    "s=open(p).read()\n"
    "for name in ['DEFAULT_FACTORY_SCENE','DEFAULT_CHECKPOINT','DEFAULT_EVAL_STEPS','DEFAULT_OBJECT_NAME']:\n"
    "    m=re.search(name+r'\\s*=\\s*[\"\\']([^\"\\']+)', s)\n"
    "    print(name,'=', m.group(1) if m else None)\n"
)
print(d.Dswhub().run_python(code, timeout=60))
