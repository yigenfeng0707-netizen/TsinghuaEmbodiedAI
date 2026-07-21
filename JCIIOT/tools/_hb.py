import sys
sys.path.insert(0, ".")
import tools.dswhub as d
print("HB:", d.Dswhub().run_python('import time; print("keepalive", time.time())', timeout=60).strip()[:80])
