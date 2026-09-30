"""Verifica controller efêmero sem executar builds no nó interno ou deploy Azure."""
import base64, http.cookiejar, json, subprocess, time
from pathlib import Path
from urllib.request import Request, build_opener, HTTPCookieProcessor, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

BASE='http://127.0.0.1:8080'
out=Path('evidence/validation')
out.mkdir(parents=True, exist_ok=True)
password=Path('secrets/admin_password').read_text().strip()
authorization='Basic '+base64.b64encode(('admin:'+password).encode()).decode()
opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))

def request(path, data=None, crumb=None):
    headers={'Authorization':authorization}
    if crumb: headers[crumb['crumbRequestField']]=crumb['crumb']
    if data is not None: headers['Content-Type']='application/x-www-form-urlencoded'
    return opener.open(Request(BASE+path, data=data, headers=headers), timeout=5)

def capture():
    status=subprocess.run(['docker','compose','ps','-a'], text=True, capture_output=True)
    logs=subprocess.run(['docker','compose','logs','--no-color','--tail','300','controller'], text=True, capture_output=True)
    (out/'compose-status.txt').write_text(status.stdout+status.stderr)
    (out/'controller-startup.log').write_text(logs.stdout+logs.stderr)

last=None
for attempt in range(36):
    running=subprocess.run(['docker','compose','ps','--status','running','-q','controller'], text=True, capture_output=True).stdout.strip()
    if not running and attempt >= 2:
        capture()
        raise RuntimeError('Container Jenkins parou durante a inicialização; consultar artefato controller-startup.log')
    try:
        with request('/computer/api/json') as response:
            computers=json.load(response)['computer']
        break
    except Exception as error:
        last=repr(error)
        time.sleep(5)
else:
    capture()
    raise RuntimeError('Controller não respondeu em 180 segundos; última resposta: '+str(last))

try:
    urlopen(BASE+'/api/json', timeout=5)
except HTTPError as error:
    assert error.code in (401,403), 'Status inesperado para acesso anônimo'
else:
    raise AssertionError('Acesso anônimo indevidamente liberado')

builtin=[node for node in computers if node['displayName'] not in ('ubuntu-ci','ubuntu-release')]
assert len(builtin)==1 and builtin[0]['numExecutors']==0
nodes={node['displayName']:node['numExecutors'] for node in computers}
assert nodes['ubuntu-ci']==2 and nodes['ubuntu-release']==1
with request('/crumbIssuer/api/json') as response:
    crumb=json.load(response)

proof={'controllerStarted':True,'anonymousReadBlocked':True,'nodes':nodes,'pipelineValidation':{}}
for file in ('Jenkinsfile','Jenkinsfile.ci'):
    payload=urlencode({'jenkinsfile':Path(file).read_text()}).encode()
    with request('/pipeline-model-converter/validate', payload, crumb) as response:
        result=response.read().decode()
    print(file+': '+result.strip())
    assert 'Jenkinsfile successfully validated.' in result
    proof['pipelineValidation'][file]=result.strip()

capture()
(out/'controller-check.json').write_text(json.dumps(proof,indent=2))
print('PASS: controller iniciou, anônimo bloqueado, zero executores internos, agents configurados e pipelines válidas')
