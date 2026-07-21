import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/models/obs_core.py'\n"
    "src=open(p).read()\n"
    "print(src[:1200])\n"
    "print('=== backbones refs ===')\n"
    "for m in re.finditer(r'ResNet|backbone_class|OBS_ENCODER_BACKBONES|register|Backbone', src): i=m.start(); print(src[max(0,i-50):i+60].replace(chr(10),' '))\n"
)
print(d.Dswhub().run_python(code, timeout=60))
