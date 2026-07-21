import sys
sys.path.insert(0, ".")
import tools.dswhub as d

recon = (
    "echo '=== which python ==='; which python python3; "
    "echo '=== sys-py imports ==='; python3 -c 'import mujoco,robosuite; print(\"mujoco\",mujoco.__version__,\"robosuite\",robosuite.__version__)' 2>&1; "
    "echo '=== dist-packages ==='; ls /usr/local/lib/python3.12/dist-packages/ | grep -iE 'mujoco|robomimic|robosuite'; "
    "echo '=== conda envs ==='; ls /opt/conda/envs 2>/dev/null; which conda; "
    "echo '=== pip show robomimic ==='; pip show robomimic 2>&1 | head -4; "
    "echo '=== PYTHONPATH ==='; echo \"PYTHONPATH=$PYTHONPATH\"; "
    "echo '=== git remote ==='; cd /mnt/workspace/JCIIOT_repo && git remote -v; "
    "echo '=== JCIIOT dir ==='; ls /mnt/workspace/JCIIOT_repo/JCIIOT | head -40; "
    "echo '=== rocm ==='; ls /opt/rocm 2>/dev/null | head; "
    "echo '=== END ===' "
)
# write a script to instance and execute via terminal, redirect to a file
script = "cat > /mnt/workspace/_recon.sh <<'EOF'\n" + recon + "\nEOF\nbash /mnt/workspace/_recon.sh > /mnt/workspace/_recon.out 2>&1\n"

c = d.Dswhub()
c.run_in_terminal(script, wait=10)

# read back the file
try:
    out = c.contents("_recon.out", content=1).get("content", "")
    print(out)
except Exception as e:
    print("read err", e)
