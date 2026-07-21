import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os, urllib.request, json\n"
    "base='https://open.bigmodel.cn/api/paas/v4/'\n"
    "key='608e441d08264fa98257baf063c6a7b7.Ko08EDn4wCaO5QS8'\n"
    "body=json.dumps({'model':'glm-5.2','messages':[{'role':'user','content':'Reply with exactly: PONG'}],'max_tokens':32}).encode()\n"
    "req=urllib.request.Request(base+'chat/completions', data=body, headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})\n"
    "r=urllib.request.urlopen(req, timeout=40)\n"
    "j=json.load(r)\n"
    "print('FULL RESP:', json.dumps(j, ensure_ascii=False)[:400])\n"
)
print(d.Dswhub().run_python(code, timeout=90))
