import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py'\n"
    "s=open(p).read()\n"
    "old='            try:\\n                _set_viewer_camera(self._env, \"birdview\", render_once=True)\\n            except Exception:\\n                pass'\n"
    "new='            if not self._headless:\\n                try:\\n                    _set_viewer_camera(self._env, \"birdview\", render_once=True)\\n                except Exception:\\n                    pass'\n"
    "assert old in s, 'pattern not found'\n"
    "s=s.replace(old,new,1)\n"
    "open(p,'w').write(s)\n"
    "print('patched headless viewer guard')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
