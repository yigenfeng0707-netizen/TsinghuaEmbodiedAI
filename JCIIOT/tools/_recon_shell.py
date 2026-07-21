import sys
sys.path.insert(0, ".")
import tools.dswhub as d

cmd = (
    "which python python3; "
    "python3 -c 'import mujoco,robosuite; print(\"sys-py mujoco\",mujoco.__version__,\"robosuite\",robosuite.__version__)' 2>&1; "
    "ls /usr/local/lib/python3.12/dist-packages/ | grep -iE 'mujoco|robomimic|robosuite' ; "
    "echo '--- conda ---'; ls /opt/conda/envs 2>/dev/null; "
    "echo '--- pip show ---'; pip show robomimic 2>&1 | head -3; "
    "echo '--- PYTHONPATH in profile ---'; cat ~/.bashrc 2>/dev/null | grep -i pythonpath; "
    "cat /root/.bashrc 2>/dev/null | grep -i pythonpath; "
    "echo '--- git remote ---'; cd /mnt/workspace/JCIIOT_repo && git remote -v; "
    "echo '--- cwd contents ---'; ls /mnt/workspace/JCIIOT_repo/JCIIOT | head -40"
)

c = d.Dswhub()
term, buf = c.run_in_terminal(cmd, wait=12)
print(buf)
