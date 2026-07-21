import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os, urllib.request, json\n"
    "base='https://open.bigmodel.cn/api/paas/v4/'\n"
    "key='608e441d08264fa98257baf063c6a7b7.Ko08EDn4wCaO5QS8'\n"
    "def chat(model, content, sys=None):\n"
    "    msgs=[]\n"
    "    if sys: msgs.append({'role':'system','content':sys})\n"
    "    msgs.append({'role':'user','content':content})\n"
    "    body=json.dumps({'model':model,'messages':msgs,'max_tokens':64}).encode()\n"
    "    req=urllib.request.Request(base+'chat/completions', data=body, headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})\n"
    "    try:\n"
    "        r=urllib.request.urlopen(req, timeout=40)\n"
    "        j=json.load(r)\n"
    "        return 'OK: '+j['choices'][0]['message']['content'][:80]\n"
    "    except Exception as e:\n"
    "        return 'ERR: '+str(e)[:300]\n"
    "print('TEXT glm-5.2 ->', chat('glm-5.2','Say hello in 5 words.'))\n"
    "print('VLM GLM-5V-Turbo ->', chat('GLM-5V-Turbo','Describe a red cube in one sentence.'))\n"
)
print(d.Dswhub().run_python(code, timeout=120))
