import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INSTALL = r'''#!/bin/bash
set -e
echo "=== apt install osmesa + xvfb ==="
sudo apt-get update -qq 2>&1 | tail -2
sudo apt-get install -y -qq libosmesa6 libgl1-mesa-dev libglew-dev xvfb libxinerama1 libxcursor1 libxrandr2 2>&1 | tail -5
echo "=== pip install core ==="
pip install -q "mujoco==3.10.0" termcolor matplotlib h5py PyOpenGL imageio imageio-ffmpeg 2>&1 | tail -3
echo "=== pip install robomimic deps ==="
pip install -q tensorboard tensorboardX einops filters pyyaml tqdm psutil 2>&1 | tail -3
echo "=== pip install glfw (for offscreen fallback) ==="
pip install -q glfw 2>&1 | tail -2
echo "=== pip install -e robomimic (no deps) ==="
cd /mnt/workspace/JCIIOT_repo/JCIIOT/robomimic && pip install -e . --no-deps 2>&1 | tail -3
echo "=== pip install -e robosuite (no deps) ==="
cd /mnt/workspace/JCIIOT_repo/JCIIOT/robosuite && pip install -e . --no-deps 2>&1 | tail -3
echo "=== verify ==="
cd /mnt/workspace/JCIIOT_repo/JCIIOT
python -c "import mujoco,robosuite,robomimic,h5py,OpenGL,imageio,tensorboard; print('ALL IMPORTS OK'); import os;print('MUJOCO test:', mujoco.__version__)"
ls /usr/lib/x86_64-linux-gnu/libOSMesa.so.8 && echo "OSMESA OK"
which xvfb-run && echo "XVFB OK"
echo "=== DONE ==="
'''

c = d.Dswhub()
c.s.put(d.BASE+"/api/contents/_install.sh",
        json={"type":"file","format":"text","content":INSTALL}, timeout=30)
launch = (
    "import subprocess,os\n"
    "env={**os.environ}\n"
    "p=subprocess.Popen(['bash','/mnt/workspace/_install.sh'],stdout=open('/mnt/workspace/_install.log','w'),stderr=subprocess.STDOUT,env=env)\n"
    "print('LAUNCHED',p.pid)\n"
)
print(c.run_python(launch, timeout=30))
