import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py'\n"
    "src=open(p).read()\n"
    "import re\n"
    "print('LINES', len(src.splitlines()))\n"
    "for m in re.finditer(r'def |argparse|add_argument|checkpoint|__main__|sys.argv', src): i=m.start(); print(src[max(0,i-10):i+70].replace(chr(10),' '))\n"
)
print(d.Dswhub().run_python(code, timeout=60))
