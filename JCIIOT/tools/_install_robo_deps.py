import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,sys\n"
    "pkgs='imageio imageio-ffmpeg tensorboard tensorboardX einops filters pyyaml tqdm h5py psutil'\n"
    "r=subprocess.run([sys.executable,'-m','pip','install',*pkgs.split()],capture_output=True,text=True,timeout=600)\n"
    "print('rc',r.returncode); print(r.stdout[-400:]); print('ERR',r.stderr[-300:])\n"
)
print(d.Dswhub().run_python(code, timeout=650))
