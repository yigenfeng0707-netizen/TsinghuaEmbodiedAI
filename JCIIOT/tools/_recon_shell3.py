import sys
sys.path.insert(0, ".")
import tools.dswhub as d

recon = (
    "echo '=== all pythons ==='; ls -la /usr/bin/python* /usr/local/bin/python* 2>/dev/null; "
    "echo '=== pip path ==='; which pip pip3; pip --version 2>&1; "
    "echo '=== find mujoco pkg ==='; find / -name 'mujoco' -maxdepth 8 -type d 2>/dev/null | head; "
    "echo '=== find robomimic pkg ==='; find / -name 'robomimic' -maxdepth 8 -type d 2>/dev/null | head; "
    "echo '=== venvs ==='; ls -d /root/*venv* /opt/*venv* /mnt/workspace/*venv* 2>/dev/null; ls /opt/conda 2>/dev/null; "
    "echo '=== env of default shell (from run_all context) ==='; cat /mnt/workspace/run_all.log | head -1; "
    "echo '=== login shell profile ==='; cat ~/.bash_profile 2>/dev/null; cat ~/.profile 2>/dev/null | head -20; "
    "echo '=== frontmatter of run_all.sh shebang did /bin/bash; check sourced ==='; head -1 /mnt/workspace/run_all.sh; "
    "echo '=== where does run_all python resolve ==='; source ~/.bashrc 2>/dev/null; which python; python -c 'import mujoco; print(mujoco.__version__)' 2>&1 | head -2; "
    "echo '=== END ===' "
)
script = "cat > /mnt/workspace/_recon2.sh <<'EOF'\n" + recon + "\nEOF\nbash /mnt/workspace/_recon2.sh > /mnt/workspace/_recon2.out 2>&1\n"
c = d.Dswhub()
c.run_in_terminal(script, wait=12)
try:
    print(c.contents("_recon2.out", content=1).get("content", ""))
except Exception as e:
    print("read err", e)
